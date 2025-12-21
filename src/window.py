from gi.repository import Adw, Gtk, Gdk, GLib

from .timerlabel import CubeTimerLabel
from .scramble import Scramble
from .score import ScoresColumnView
from .timercontroller import TimerController

@Gtk.Template(resource_path='/io/github/vallabhvidy/CubeTimer/window.ui')
class CubeTimerWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'CubeTimerWindow'

    cube_timer_label = Gtk.Template.Child()
    header_bar_menu = Gtk.Template.Child()
    scramble = Gtk.Template.Child()
    split_view = Gtk.Template.Child()
    show_sidebar_button = Gtk.Template.Child()
    scores_column_view = Gtk.Template.Child()
    puzzle_dropdown = Gtk.Template.Child()
    breakpoint_step1 = Gtk.Template.Child()
    breakpoint_step3 = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.controller = TimerController(Gdk.KEY_space)

        self.widgets = [
            self.puzzle_dropdown,
            self.scramble,
            self.show_sidebar_button
        ]

        self.controller.connect("idle", self.idle)
        self.controller.connect("red", self.red)
        self.controller.connect("green", self.green)
        self.controller.connect("solving", self.solving)
        self.controller.connect("solved", self.solved)

        # key press events
        def key_press(event, keyval, keycode, state):
            return self.controller.key_press(keyval)

        def key_release(event, keyval, keycode, state):
            return self.controller.key_release(keyval)

        evk = Gtk.EventControllerKey()
        evk.connect("key-pressed", key_press)
        evk.connect("key-released", key_release)
        evk.set_propagation_phase(1)
        self.add_controller(evk)

        # puzzle selection dropdown
        def on_dropdown_activate(dropdown, pspec):
            selected = dropdown.props.selected_item.get_string()
            self.scramble.update_scramble(selected)
        self.puzzle_dropdown.connect("notify::selected-item", on_dropdown_activate)

        def scramble_change_scale(bp, scale):
            self.scramble.scale_factor = scale
            self.scramble.update_label()
        for i in (self.breakpoint_step1, self.breakpoint_step3):
            i.connect("apply", scramble_change_scale, 0.75)
            i.connect("unapply", scramble_change_scale, 1)

    def idle(self, inst):
        self.cube_timer_label.set_colored_label()

    def red(self, inst):
        self.cube_timer_label.set_colored_label(color="red")

    def green(self, inst):
        self.cube_timer_label.set_colored_label(time=0, color="green")
        self.sidebar_state = self.split_view.get_show_sidebar()
        self.split_view.set_show_sidebar(False)
        for widget in self.widgets:
            widget.set_visible(False)

    def solving(self, inst, time):
        self.cube_timer_label.set_colored_label(time=time)

    def solved(self, inst, time):
        self.split_view.set_show_sidebar(self.sidebar_state)
        self.scores_column_view.add_score(time, self.scramble.scramble)
        self.scramble.update_scramble()
        for widget in self.widgets:
            widget.set_visible(True)
