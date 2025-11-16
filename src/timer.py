from gi.repository import Adw
from gi.repository import Gtk, GLib, GObject

time = GLib.get_monotonic_time

state = True

delay = 0.20

class CubeTimer(GObject.Object):
    __gtype_name__ = 'CubeTimer'

    def __init__(self, update_label, **kwargs):
        super().__init__(**kwargs)
        self.time = 0
        self.timer_running = False
        self.space_pressed = False
        self.space_released = True
        self.drop_down = None
        self.update_label = update_label
        self.update_scores = None
        self.scramble = None
        self.get_set = False
        self.sidebar_button = None
        self.split_view_state = True

    def start_timer(self):
        self.timer_running = True
        self.update_label()
        GLib.timeout_add(10, self.update_timer)

    def update_timer(self):
        self.time += 1
        self.update_label()

        return self.timer_running

    def stop_timer(self):
        self.scramble.show_scramble()
        self.sidebar_button.set_visible(True)
        self.drop_down.set_visible(True)
        self.timer_running = False
        self.split_view.set_show_sidebar(state)
        self.update_scores(self.time, self.scramble.scramble)

    def key_press(self, event, keyval, keycode, state):
        if keyval == ord(' '):
            if not self.timer_running and not self.space_pressed:
                self.update_label("red")
                self.space_pressed = True
                self.space_pressed_time = time()
            elif self.timer_running:
                self.stop_timer()
            elif self.space_pressed:
                if time() - self.space_pressed_time >= delay:
                    self.reset_timer()
                    state = bool(self.split_view.get_show_sidebar())
                    self.split_view.set_show_sidebar(False)
                    self.scramble.hide_scramble()
                    self.drop_down.set_visible(False)
                    self.sidebar_button.set_visible(False)
                    self.update_label("green")
                    self.get_set = True
        elif self.timer_running:
            self.stop_timer()

    def key_released(self, event, keyval, keycode, state):
        if self.space_pressed:
            if self.get_set:
                self.start_timer()
                self.scramble.update_scramble()
                self.get_set = False
            self.space_pressed = False
            self.update_label()

    def reset_timer(self):
        self.time = 0




