from gi.repository import GObject
from .preferences import settings
from .utils import scores_file_path, data_dir
import json
import sqlite3

db_path = data_dir / 'scores.db'

# deprecated
class ScoresModel(GObject.Object):
    @GObject.Signal
    def refresh(self):
        pass

    def __init__(self, **kargs):
        super().__init__(**kargs)
        self.path = scores_file_path
        self.sessions = {}
        self.load()
        self.wca_avg = settings.get_boolean("wca-avg")
        settings.connect("changed::wca-avg", self.update_wca_avg)

    def load(self):
        # for backward compatibility
        def modscore(score, version):
            if version == 2:
                return score

            # for version 0 where mins, secs and milisecs were
            # stored separately
            if "min" in score:
                score["time"] = score["min"] * 6000 + score["sec"] * 100 + score["mili"]
                score.pop("min", None)
                score.pop("sec", None)
                score.pop("mili", None)
                score.pop("ao5", None)
                score.pop("ao12", None)
                score["time"] *= 10
                return score

            # version 1 where times were stored in
            # centiseconds
            if version == 1 and "time" in score:
                score["time"] *= 10
                return score

            return score

        try:
            with open(self.path, 'r') as scores_file:
                sessions = json.load(scores_file)
                self.sessions["last-session"] = sessions.get("last-session", _("Session 1"))
                version = sessions.get("version", 1)
                for session in sessions:
                    if session == "last-session" or session == "version":
                        continue
                    self.sessions[session] = []
                    for score in sessions[session]:
                        self.sessions[session].append(modscore(score, version))

        except FileNotFoundError:
            print(_("scores.json not found."))
            self.sessions = {_("Session 1"): [], "last-session": _("Session 1"), "version": 2}

        self.save()

    def save(self):
        self.sessions["version"] = 2
        with open(self.path, "w") as scores_file:
            json.dump(self.sessions, scores_file)

    def set_last_session(self, session):
        self.sessions["last-session"] = session
        self.save()

    def get_session(self, session):
        return self.sessions[session]

    def get_score(self, session, index):
        return self.sessions[session][index]

    def get_all_sessions(self):
        not_sessions = ("last-session", "version")
        sessions = [session for session in self.sessions.keys() if session not in not_sessions]
        return sessions

    def get_last_session(self):
        return self.sessions["last-session"]

    def add_session(self, session):
        self.sessions[session] = []
        self.set_last_session(session)
        self.save()

    def rename_session(self, new_session, old_session):
        self.sessions[new_session] = self.sessions.pop(old_session)
        self.save()

    def remove_session(self, session):
        self.sessions.pop(session, None)
        self.save()

    def add_score(self, session, score):
        self.sessions[session].append(score)
        self.save()

    def delete_score(self, session, index):
        self.sessions[session].pop(index)
        self.save()

    def dnf_score(self, session, index):
        self.sessions[session][index]["time"] = 0
        self.save()

    def update_wca_avg(self, settings, key_changed):
        self.wca_avg = settings.get_boolean("wca-avg")
        self.emit("refresh")

    def calculate_average(self, session, index, n):
        index = index if index != -1 else len(self.sessions[session])-1

        if index + 1 < n:
            return -1

        times = []
        dnf = 0
        for i in range(index, index-n, -1):
            dnf += (self.sessions[session][i]["time"] == 0)
            times.append(self.sessions[session][i]["time"])

        if dnf >= 2:
            return 0

        if n < 5:
            if dnf > 0:
                return 0
            else:
                return sum(times) // n;

        if self.wca_avg:
            if dnf == 1:
                times.remove(0)
                times.remove(min(times))
            else:
                times.remove(max(times))
                times.remove(min(times))

        tot = sum(times)

        return tot // len(times)



class ScoresDB(GObject.Object):
    @GObject.Signal
    def refresh(self):
        pass

    def __init__(self, **kargs):
        super().__init__(**kargs)
        self.load()
        self.wca_avg = settings.get_boolean("wca-avg")
        settings.connect("changed::wca-avg", self.update_wca_avg)

    def load(self):
        try:
            self.conn = sqlite3.connect(db_path)
            self.c = self.conn.cursor()

            # get the list of created tables
            # https://stackoverflow.com/questions/305378/how-do-i-get-a-list-of-tables-the-schema-a-dump-using-the-sqlite3-api
            # https://stackoverflow.com/questions/4098008/create-table-in-sqlite-only-if-it-doesnt-exist-already
            # create tables if they do not exist
            # primary keys on multiple columns
            # https://stackoverflow.com/questions/734689/sqlite-primary-key-on-multiple-columns
            # foreign key on session_id
            # https://www.sqlitetutorial.net/sqlite-foreign-key/
            # enable foreign keys
            self.c.execute("pragma foreign_keys = ON")
            self.c.execute("""
                create table if not exists sessions (
                session_id integer primary key,
                name text unique
                )
            """)
            self.c.execute("""
                create table if not exists scores (
                score_id integer primary key,
                session_id integer,
                time integer,
                scramble text,
                foreign key (session_id)
                    references sessions (session_id)
                        on delete cascade
                )
            """)
            # https://www.sqlitetutorial.net/sqlite-index/
            # create index on session
            self.c.execute("""
                create index if not exists session_idx
                on scores(session_id)
            """)
            # insert a default session called 'Session 1'
            # and set it as the last session
            # if no sessions are found
            default_session = _("Session 1")
            if self.c.execute("select 1 from sessions limit 1").fetchone() is None:
                self.c.execute("""
                    insert into sessions (name)
                    values (?)
                """, (default_session,))
                self.set_last_session(default_session)

            # https://www.sqlitetutorial.net/sqlite-window-functions/sqlite-row_number/
            # https://www.sqlitetutorial.net/sqlite-create-view/
            # create view
            self.c.execute("""
                create view if not exists score_session
                as
                select
                    row_number() over (
                        partition by a.session_id
                        order by a.score_id
                    ) - 1 as score_index,
                    a.score_id as score_id,
                    a.time as time,
                    a.scramble as scramble,
                    b.name as session
                from
                    scores as a
                inner join sessions as b on a.session_id=b.session_id
            """)

            self.save()
        except Exception:
            print("error")

    def save(self):
        # https://stackoverflow.com/questions/8030779/change-sqlite-database-version-number
        self.c.execute("pragma user_version = 3")
        self.conn.commit()

    def set_last_session(self, session):
        settings.set_string("last-session", session)

    def get_session(self, session):
        # https://stackoverflow.com/questions/45965007/multiline-f-string-in-python
        # https://www.sqlitetutorial.net/sqlite-join/
        res = self.c.execute("""
            select time, scramble
            from score_session
            where session=?
        """, (session,))

        times = res.fetchall()

        return self.list_of_dictionary(times)

    def list_of_dictionary(self, list_of_tuples) -> list[dict]:
        return [ { "time": e[0], "scramble": e[1] } for e in list_of_tuples ]

    def get_latest_score_index(self, session):
        res = self.c.execute("""
            select score_index
            from score_session
            where session=?
            order by score_index desc
            limit 1
        """, (session,))

        return res.fetchone()[0]

    def get_score(self, session, index):
        if index == -1:
            index = self.get_latest_score_index(session)

        print(index)

        res = self.c.execute("""
            select time, scramble
            from score_session
            where score_index=? and session=?
        """, (index, session,))

        score = res.fetchone()

        return {"time": score[0], "scramble": score[1]}

    def get_all_sessions(self):
        res = self.c.execute("select name from sessions")
        sessions = [ session[0] for session in res.fetchall() ]
        return sessions

    def get_last_session(self):
        return settings.get_string("last-session")

    def add_session(self, session):
        # https://www.sqlitetutorial.net/sqlite-insert/
        self.c.execute("""
            insert into sessions (name)
            values (?)
        """, (session,))
        self.set_last_session(session)
        self.save()

    def rename_session(self, new_session, old_session):
        # https://www.sqlitetutorial.net/sqlite-update/
        self.c.execute("""
            update sessions
            set name=?
            where name=?
        """, (new_session, old_session,))
        self.save()

    def remove_session(self, session):
        # https://www.sqlitetutorial.net/sqlite-delete/
        self.c.execute("""
            delete from sessions
            where name=?
        """, (session,))
        self.save()

    def add_score(self, session, score):
        time = score["time"]
        scramble = score["scramble"]
        res = self.c.execute("select session_id from sessions where name=?", (session,))
        row = res.fetchone()
        if not row:
            self.add_session(session)
            res = self.c.execute("select session_id from sessions where name=?", (session,))
            row = res.fetchone()

        session_id = row[0]

        self.c.execute("""
            insert into scores (session_id, time, scramble)
            values (?, ?, ?)
        """, (session_id, time, scramble,))

        self.save()

    def delete_score(self, session, index):
        res = self.c.execute("""
            select score_id
            from score_session
            where session=? and score_index=?
        """, (session, index,))
        score_id = res.fetchone()[0]
        self.c.execute("""
            delete from scores
            where score_id=?
        """, (score_id,))
        self.save()

    def dnf_score(self, session, index):
        res = self.c.execute("""
            select score_id
            from score_session
            where session=? and score_index=?
        """, (session, index,))
        score_id = res.fetchone()[0]
        self.c.execute("""
            update scores
            set time=0
            where score_id=?
        """, (score_id,))
        self.save()

    def update_wca_avg(self, settings, key_changed):
        self.wca_avg = settings.get_boolean("wca-avg")
        self.emit("refresh")

    def calculate_average(self, session, index, limit):
        """
        calculate the average of last n solves from index.
        wca averages ignore the best and worst solves while
        calculating average.
        if there are more than 1 dnf then the entire average
        is dnf.
        """
        # https://www.sqlitetutorial.net/sqlite-limit/
        # consider rows which have score_index <= give index
        # sort all scores in descending
        # then limit till n

        if index == -1:
            index = self.get_latest_score_index(session)

        res = self.c.execute("""
            select time
            from score_session
            where session=? and score_index<=?
            order by score_index desc
            limit ?
        """, (session, index, limit))

        times = [ time[0] for time in res.fetchall() ]
        dnf = sum([ int(time==0) for time in times ])

        if len(times) < limit:
            return -1

        if dnf >= 2:
            return 0

        if limit < 5:
            if dnf > 0:
                return 0
            else:
                return sum(times) // limit;

        if self.wca_avg:
            if dnf == 1:
                times.remove(0)
                times.remove(min(times))
            else:
                times.remove(max(times))
                times.remove(min(times))

        tot = sum(times)

        return tot // len(times)
