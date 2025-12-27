from gi.repository import GObject, GLib, Gdk

from .timer import Timer
from .preferences import settings

time = GLib.get_monotonic_time
delay = 200

class TimerController(GObject.Object):
    __gtype_name__ = "TimeController"

    @GObject.Signal
    def idle(self):
        pass

    @GObject.Signal
    def red(self):
        pass

    @GObject.Signal
    def green(self):
        pass

    @GObject.Signal
    def solving(self, time: int):
        pass

    @GObject.Signal
    def solved(self, time: int):
        pass

    def __init__(self, **kargs):
        super().__init__(**kargs)

        self.timer = Timer()
        self.timer_key = Gdk.KEY_space

        self.timer.connect("update", lambda inst: self.emit("solving", self.timer.time))
        self.timer.connect("stop", lambda inst: self.emit("solved", self.timer.time))

        self.hold = settings.get_boolean("hold-to-start")
        self.wca = settings.get_boolean("wca-inspection")
        self.any_key = settings.get_boolean("stop-timer-any-key")

        settings.connect("changed", self.update_settings)

        # 0 - idle
        # 1 - red
        # 2 - green
        # 3 - running
        self.state = 0

        # 0 - idle
        # 1 - green
        # 2 - running
        self.wca_state = 0

    def update_settings(self, settings, key_changed):
        self.hold = settings.get_boolean("hold-to-start")
        self.wca = settings.get_boolean("wca-inspection")
        self.any_key = settings.get_boolean("stop-timer-any-key")

    def ready(self):
        self.emit("green")
        self.timer.reset_timer()
        self.state = 2

    def start(self):
        self.timer.emit("start")
        self.timer.start_timer()
        self.state = 3

    def halt(self):
        self.timer.stop_timer()
        self.state = 0

    def key_press(self, keyval):
        # if timer is running stop it
        if self.state == 3 and (self.any_key or keyval == self.timer_key):
            self.halt()
            return True

        # if space is press
        elif keyval == self.timer_key:
            # if self.wca:
            #     self.state = 1
            #     self.emit("wca", self.time)

            if self.hold:
                if self.state == 1:
                    # green
                    if time() - self.key_pressed_time >= delay:
                        self.ready()
                # red
                elif self.state == 0:
                    self.state = 1
                    self.emit("red")
                    self.key_pressed_time = time()

            # if there is no hold directly change state to green
            else:
                if self.state == 0:
                    self.ready()
            return True

        return False

    def key_release(self, keyval):
        # print("key released...")
        if keyval == self.timer_key:
            if self.state == 1:
                self.emit("idle")
                self.state = 0
            if self.state == 2:
                self.start()
            return True

        return False
