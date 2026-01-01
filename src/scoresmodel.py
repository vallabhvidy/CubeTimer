from gi.repository import GObject
from .preferences import settings
from .utils import scores_file_path
import json

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

    def p2_score(self, session, index):
        if self.sessions[session][index]["time"] == 0:
            return
        self.sessions[session][index]["time"] += 2_000
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
