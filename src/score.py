from gi.repository import Gtk, GLib, GObject, Gio, Adw
from collections import deque
from .preferences import settings
from .utils import time_string, MAX_TIME
from .scoresmodel import ScoresDB
from .lrucache import LRUCache
import json

class Scores(GObject.Object):
    index: int = GObject.Property(type=int)
    time_ms: int = GObject.Property(type=int)
    mo3: int = GObject.Property(type=int)
    ao5: int = GObject.Property(type=int)
    ao12: int = GObject.Property(type=int)

    def __init__(self, index: int, time_ms: int = -1, mo3: int = -1, ao5: int = -1, ao12: int = -1):
        super().__init__()
        self.index = index
        self.time_ms = time_ms
        self.mo3 = mo3
        self.ao5 = ao5
        self.ao12 = ao12

class Session(GObject.Object):
    name: str = GObject.Property(type=str)

    def __init__(self, name: str):
        super().__init__()
        self.name = name

@Gtk.Template(resource_path='/io/github/vallabhvidy/CubeTimer/score.ui')
class ScoresColumnView(Gtk.Box):
    __gtype_name__ = "ScoresColumnView"

    scores_column_view = Gtk.Template.Child()
    dialog = Gtk.Template.Child()
    time_row = Gtk.Template.Child()
    scramble_row = Gtk.Template.Child()
    sessions_drop_down = Gtk.Template.Child()
    scrolled_window = Gtk.Template.Child()
    best_time = Gtk.Template.Child()
    best_mo3 = Gtk.Template.Child()
    best_ao5 = Gtk.Template.Child()
    best_ao12 = Gtk.Template.Child()
    current_time = Gtk.Template.Child()
    current_mo3 = Gtk.Template.Child()
    current_ao5 = Gtk.Template.Child()
    current_ao12 = Gtk.Template.Child()
    add_session_button = Gtk.Template.Child()
    add_session_dialog = Gtk.Template.Child()
    session_name = Gtk.Template.Child()
    rename_session_button = Gtk.Template.Child()
    rename_session_dialog = Gtk.Template.Child()
    session_rename = Gtk.Template.Child()
    remove_session_button = Gtk.Template.Child()
    remove_session_dialog = Gtk.Template.Child()

    @GObject.Signal
    def refresh(self):
        pass

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.model = ScoresDB()
        self.current_session = self.model.get_last_session()
        self.store = Gio.ListStore()
        self.sort_model = Gtk.SortListModel()
        self.select = Gtk.SingleSelection()
        self.scores = []
        self.selected_index = 0
        self.cache = LRUCache(5)

        self.wca_avg = settings.get_boolean("wca-avg")
        settings.connect("changed::wca-avg", self.update_wca_avg)

        self.sessions_store = Gio.ListStore()

        self.build_drop_down()
        self.build_column_view()
        self.build_dialog()
        self.build_sessions_menu()

        self.time_ms = 0
        self.dq3 = deque(maxlen=3)
        self.dq5 = deque(maxlen=5)
        self.dq12 = deque(maxlen=12)

        self.load_session(self.current_session)
        self.select.set_selected(0)
        self.scroll_to_top()

        self.model.connect("refresh", lambda inst: self.reload_scores())

    def update_wca_avg(self, settings, key_changed):
        self.wca_avg = settings.get_boolean("wca-avg")
        self.emit("refresh")
        self.reload_scores()

    def build_sessions_menu(self):
        def rebuild_drop_down():
            self.sessions_store.remove_all()
            sessions = self.model.get_all_sessions()
            for session in sessions:
                self.sessions_store.append(Session(session))

        def remove_session(widget, response):
            if response != "delete":
                return

            self.model.remove_session(self.current_session)
            rebuild_drop_down()
            if len(self.sessions_store) == 0:
                self.model.add_session(_("Session 1"))
                rebuild_drop_down()
                self.load_session(_("Session 1"))
            else:
                self.load_session(self.sessions_store[-1].name)

        def rename_session(widget, response):
            if response != "rename":
                return

            session_name = self.session_rename.get_buffer().get_text()
            self.model.rename_session(session_name, self.current_session)
            rebuild_drop_down()
            self.load_session(session_name)

        def add_session(widget, response):
            if response != "add":
                return

            session_name = self.session_name.get_buffer().get_text()
            self.model.add_session(session_name)
            self.sessions_store.append(Session(session_name))
            self.load_session(session_name)

        def validate_name(entry):
            session_name = entry.get_buffer().get_text()

            if len(session_name) == 0 or session_name in self.model.get_all_sessions() or session_name == "last-session":
                self.add_session_dialog.set_response_enabled("add", False)
                self.session_name.remove_css_class("success")
                self.session_name.add_css_class("error")
            else:
                self.add_session_dialog.set_response_enabled("add", True)
                self.session_name.remove_css_class("error")
                self.session_name.add_css_class("success")

        def validate_rename(entry):
            session_rename = entry.get_buffer().get_text()

            if len(session_rename) == 0 or session_rename in self.model.get_all_sessions() or session_rename == "last-session":
                self.rename_session_dialog.set_response_enabled("rename", False)
                self.session_rename.remove_css_class("success")
                self.session_rename.add_css_class("error")
            else:
                self.rename_session_dialog.set_response_enabled("rename", True)
                self.session_rename.remove_css_class("error")
                self.session_rename.add_css_class("success")

        def add_session_button_clicked(button):
            self.session_name.get_buffer().delete_text(0, -1)
            self.session_name.remove_css_class("success")
            self.session_name.remove_css_class("error")
            self.add_session_dialog.present(button)

        def remove_session_button_clicked(button):
            self.remove_session_dialog.set_heading(_("Delete {session}?").format(session=self.current_session))
            self.remove_session_dialog.present(button)

        def rename_session_button_clicked(button):
            self.session_rename.get_buffer().delete_text(0, -1)
            self.session_rename.remove_css_class("success")
            self.session_rename.remove_css_class("error")
            self.rename_session_dialog.present(button)

        self.add_session_button.connect("clicked", add_session_button_clicked)
        self.rename_session_button.connect("clicked", rename_session_button_clicked)
        self.remove_session_button.connect("clicked", remove_session_button_clicked)

        self.session_name.connect("changed", validate_name)
        self.session_rename.connect("changed", validate_rename)

        self.add_session_dialog.connect("response", add_session)
        self.remove_session_dialog.connect("response", remove_session)
        self.rename_session_dialog.connect("response", rename_session)

        self.add_session_dialog.set_response_enabled("add", False)
        self.rename_session_dialog.set_response_enabled("rename", False)

    def build_drop_down(self):
        def on_selected_item(dropdown, selected):
            selected_item = dropdown.get_selected_item()
            if selected_item is None:
                return
            if selected_item.name == self.current_session:
                return
            self.load_session(selected_item.name)

        fact = Gtk.SignalListItemFactory()

        def f_setup(fact, item):
            label = Gtk.Label(halign=Gtk.Align.START)
            label.set_selectable(False)
            label.set_ellipsize(3)
            item.set_child(label)

        def f_bind(fact, item):
            item.get_child().set_label(str(item.get_item().name))

        fact.connect("setup", f_setup)
        fact.connect("bind", f_bind)

        self.sessions_drop_down.set_factory(fact)
        self.sessions_drop_down.set_model(self.sessions_store)
        sessions = self.model.get_all_sessions()
        for session in sessions:
            self.sessions_store.append(Session(session))
        self.sessions_drop_down.connect("notify::selected-item", on_selected_item)

    def load_session(self, session):
        if self.scores:
            self.cache.put(self.current_session, list(self.scores))
        self.current_session = session
        self.model.set_last_session(session)
        self.select_current_session()
        self.reload_scores(session)

    def select_current_session(self):
        for idx in range(len(self.sessions_store)):
            if self.sessions_store[idx].name == self.current_session:
                self.sessions_drop_down.set_selected(idx)
                return

    def build_column_view(self):
        def on_click(widget, index):
            index = self.store.get_n_items() - 1 - index
            item = self.scores[index]
            self.selected_index = index

            time = time_string(item['time'])
            scramble = item['scramble']
            alert_string = _("Scramble:- {scramble}\n\nTime:- {time}").format(scramble=scramble, time=time)

            self.dialog.set_heading(_("Solve No. {idx}").format(idx=index+1))
            self.time_row.set_label(time)
            self.scramble_row.set_title(scramble)

            self.dialog.present(self)

        sorter = Gtk.CustomSorter.new(lambda a, b, _ : b.index - a.index)
        self.sort_model.set_sorter(sorter)
        self.sort_model.set_model(self.store)
        self.select.set_model(self.sort_model)
        self.scores_column_view.set_model(self.select)

        fact1 = Gtk.SignalListItemFactory()
        fact2 = Gtk.SignalListItemFactory()
        fact3 = Gtk.SignalListItemFactory()
        fact4 = Gtk.SignalListItemFactory()

        def f_setup(fact, item):
            label = Gtk.Label(halign=Gtk.Align.START)
            label.set_selectable(False)
            item.set_child(label)

        fact1.connect("setup", f_setup)
        fact2.connect("setup", f_setup)
        fact3.connect("setup", f_setup)
        fact4.connect("setup", f_setup)

        def f_bind1(fact, item):
            item.get_child().set_label(str(item.get_item().index+1))

        def f_bind2(fact, item):
            time_ms = item.get_item().time_ms
            item.get_child().set_label(time_string(time_ms))

        def f_bind3(fact, item):
            ao5 = time_string(item.get_item().ao5)
            item_child = item.get_child()
            item_child.set_label(ao5)
            if ao5 == "-":
                item_child.add_css_class("dim-label")
            else:
                item_child.remove_css_class("dim-label")

        def f_bind4(fact, item):
            ao12 = time_string(item.get_item().ao12)
            item_child = item.get_child()
            item_child.set_label(ao12)
            if ao12 == "-":
                item_child.add_css_class("dim-label")
            else:
                item_child.remove_css_class("dim-label")

        fact1.connect("bind", f_bind1)
        fact2.connect("bind", f_bind2)
        fact3.connect("bind", f_bind3)
        fact4.connect("bind", f_bind4)

        col1 = Gtk.ColumnViewColumn(title=_("Sr."), factory=fact1)
        col2 = Gtk.ColumnViewColumn(title=_("Time"), factory=fact2)
        col3 = Gtk.ColumnViewColumn(title=_("ao5"), factory=fact3)
        col4 = Gtk.ColumnViewColumn(title=_("ao12"), factory=fact4)

        col1.set_fixed_width(35)
        col2.set_fixed_width(80)
        col3.set_fixed_width(80)
        col4.set_fixed_width(80)

        self.scores_column_view.append_column(col1)
        self.scores_column_view.append_column(col2)
        self.scores_column_view.append_column(col3)
        self.scores_column_view.append_column(col4)

        self.scores_column_view.connect("activate", on_click)

    def build_dialog(self):
        def on_response(widget, response):
            if response == 'delete':
                self.delete_index(self.selected_index)
            elif response == "dnf":
                self.dnf_index(self.selected_index)

        self.dialog.add_response("dnf", _("Mark DNF"))
        self.dialog.add_response("delete", _("Delete"))
        self.dialog.add_response("cancel", _("Cancel"))

        self.dialog.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)
        self.dialog.set_response_appearance("dnf", Adw.ResponseAppearance.SUGGESTED)
        self.dialog.connect('response', on_response)

    def scroll_to_top(self):
        def scroll():
            vadj = self.scrolled_window.get_vadjustment()
            vadj.set_value(vadj.get_lower())
            return False
        GLib.idle_add(scroll)

    def scroll_to_bottom(self):
        def scroll():
            vadj = self.scrolled_window.get_vadjustment()
            vadj.set_value(vadj.get_upper())
            return False
        GLib.idle_add(scroll)

    def update_averages(self, new_time_ms: int = 0, new: bool = True):
        """
        calculate and return the new
        mo3, ao5, ao12
        wca averages ignore the best and worst solves while
        calculating average.
        if there are more than 1 dnf then the entire average
        is dnf.
        """
        if new:
            self.dq3.append(new_time_ms)
            self.dq5.append(new_time_ms)
            self.dq12.append(new_time_ms)

        dnf3 = self.dq3.count(0)
        dnf5 = self.dq5.count(0)
        dnf12 = self.dq12.count(0)

        mo3, ao5, ao12 = 0, 0, 0

        if len(self.dq3) < 3:
            mo3 = -1
        elif dnf3 > 0:
            mo3 = 0
        else:
            mo3 = sum(self.dq3) // 3

        if len(self.dq5) < 5:
            ao5 = -1
        elif dnf5 > 1:
            ao5 = 0
        elif self.wca_avg:
            times = list(self.dq5)
            if dnf5 == 1:
                times.remove(0)
            else:
                times.remove(max(times))
            times.remove(min(times))
            ao5 = sum(times) // len(times)
        else:
            ao5 = sum(self.dq5) // 5

        if len(self.dq12) < 12:
            ao12 = -1
        elif dnf12 > 1:
            ao12 = 0
        elif self.wca_avg:
            times = list(self.dq12)
            if dnf12 == 1:
                times.remove(0)
            else:
                times.remove(max(times))
            times.remove(min(times))
            ao12 = sum(times) // len(times)
        else:
            ao12 = sum(self.dq12) // 12

        return mo3, ao5, ao12

    def add_score(self, time, scramble):
        score = {"time": time, "scramble": scramble}
        self.model.add_score(self.current_session, score)
        idx = self.store.get_n_items()
        self.time_ms = time
        mo3, ao5, ao12 = self.update_averages(time)

        self.scores.append(score)
        self.store.append(Scores(idx, time, mo3, ao5, ao12))
        self.select.set_selected(0)
        self.scroll_to_top()
        self.load_stats()

    def delete_index(self, index):
        self.model.delete_score(self.current_session, index)
        self.scores.pop(index)
        self.reload_scores_from_index(index)

    def dnf_index(self, index):
        self.model.dnf_score(self.current_session, index)
        self.scores[index]["time"] = 0
        self.reload_scores_from_index(index)

    def load_stats(self):
        time = self.time_ms
        mo3, ao5, ao12 = self.update_averages(new=False)

        self.current_time.set_label(time_string(time))
        self.current_mo3.set_label(time_string(mo3))
        self.current_ao5.set_label(time_string(ao5))
        self.current_ao12.set_label(time_string(ao12))

        if time > 0:
            self.min_time = min(self.min_time, time) if self.min_time > 0 else time

        if mo3 > 0:
            self.min_mo3 = min(self.min_mo3, mo3) if self.min_mo3 > 0 else mo3

        if ao5 > 0:
            self.min_ao5 = min(self.min_ao5, ao5) if self.min_ao5 > 0 else ao5

        if ao12 > 0:
            self.min_ao12 = min(self.min_ao12, ao12) if self.min_ao12 > 0 else ao12

        self.best_time.set_label(time_string(self.min_time))
        self.best_mo3.set_label(time_string(self.min_mo3))
        self.best_ao5.set_label(time_string(self.min_ao5))
        self.best_ao12.set_label(time_string(self.min_ao12))

    def reload_stats(self):
        self.min_time = -1
        self.min_mo3 = -1
        self.min_ao5 = -1
        self.min_ao12 = -1
        self.time_ms = -1

        self.dq3.clear()
        self.dq5.clear()
        self.dq12.clear()

        for i in range(len(self.scores)):
            time = self.scores[i]["time"]
            self.time_ms = time
            mo3, ao5, ao12 = self.update_averages(time)
            if time > 0:
                self.min_time = min(self.min_time, time) if self.min_time > 0 else time

            if mo3 > 0:
                self.min_mo3 = min(self.min_mo3, mo3) if self.min_mo3 > 0 else mo3

            if ao5 > 0:
                self.min_ao5 = min(self.min_ao5, ao5) if self.min_ao5 > 0 else ao5

            if ao12 > 0:
                self.min_ao12 = min(self.min_ao12, ao12) if self.min_ao12 > 0 else ao12

        labels = (
            self.current_time,
            self.current_mo3,
            self.current_ao5,
            self.current_ao12,
            self.best_time,
            self.best_mo3,
            self.best_ao5,
            self.best_ao12
        )

        for i in labels:
            i.set_label("-")

        time = self.time_ms
        mo3, ao5, ao12 = self.update_averages(new=False)

        self.current_time.set_label(time_string(time))
        self.current_mo3.set_label(time_string(mo3))
        self.current_ao5.set_label(time_string(ao5))
        self.current_ao12.set_label(time_string(ao12))

        self.best_time.set_label(time_string(self.min_time))
        self.best_mo3.set_label(time_string(self.min_mo3))
        self.best_ao5.set_label(time_string(self.min_ao5))
        self.best_ao12.set_label(time_string(self.min_ao12))

    def reload_scores_from_index(self, start: int):
        new_scores = []

        self.dq3.clear()
        self.dq5.clear()
        self.dq12.clear()

        for i in range(max(0, start-2), start):
            self.dq3.append(self.scores[i]["time"])
        for i in range(max(0, start-4), start):
            self.dq5.append(self.scores[i]["time"])
        for i in range(max(0, start-11), start):
            self.dq12.append(self.scores[i]["time"])

        for i in range(start, len(self.scores)):
            mo3, ao5, ao12 = self.update_averages(self.scores[i]["time"])
            new_scores.append(Scores(i, self.scores[i]["time"], mo3, ao5, ao12))

        self.time_ms = self.scores[-1]["time"] if len(self.scores) > 0 else -1
        self.reload_stats()

        self.store.splice(start, self.store.get_n_items() - start, new_scores)

    def reload_scores(self, session = None):
        if session is not None:
            cache = self.cache.get(session)
            if not cache:
                self.scores = self.model.get_session(session)
            else:
                self.scores = list(cache)

        self.min_time = -1
        self.min_mo3 = -1
        self.min_ao5 = -1
        self.min_ao12 = -1
        self.time_ms = -1

        self.dq3.clear()
        self.dq5.clear()
        self.dq12.clear()

        new_scores = []

        for i in range(len(self.scores)):
            time = self.scores[i]["time"]
            self.time_ms = time
            mo3, ao5, ao12 = self.update_averages(time)
            new_scores.append(Scores(i, time, mo3, ao5, ao12))

        self.store.splice(0, self.store.get_n_items(), new_scores)

        self.reload_stats()
