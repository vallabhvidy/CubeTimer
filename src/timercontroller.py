from gi.repository import GObject, GLib

from .timer import Timer

time = GLib.get_monotonic_time
delay = 0.20

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

    def __init__(self, timer_key, **kargs):
        super().__init__(**kargs)

        self.timer = Timer()
        self.timer_key = timer_key

        def solving(inst):
            self.emit("solving", self.timer.time)
        self.timer.connect("update", solving)

        # 0 - idle
        # 1 - red
        # 2 - green
        # 3 - running
        self.state = 0

    def key_press(self, keyval):
        # if timer is running stop it
        if self.state == 3:
            self.timer.stop_timer()
            self.emit("solved", self.timer.time)
            self.state = 0
            return True

        # if space is press
        elif keyval == self.timer_key:
            if self.state == 1:
                # green
                if time() - self.key_pressed_time >= delay:
                    self.emit("green")
                    self.timer.reset_timer()
                    self.state = 2
            # red
            elif self.state == 0:
                self.state = 1
                self.emit("red")
                self.key_pressed_time = time()

            return True

        return False

    def key_release(self, keyval):
        # print("key released...")
        if keyval == self.timer_key:
            if self.state == 1:
                self.emit("idle")
                self.state = 0
            if self.state == 2:
                self.timer.emit("start")
                self.timer.start_timer()
                self.state = 3
            return True

        return False
