from gi.repository import GLib, GObject
from .utils import MAX_TIME

time = GLib.get_monotonic_time

class Timer(GObject.Object):
    __gtype_name__ = "Timer"

    @GObject.Signal
    def start(self):
        pass

    @GObject.Signal
    def update(self):
        pass

    @GObject.Signal
    def stop(self):
        pass

    def __init__(self, **kargs):
        super().__init__(**kargs)

        self.time = 0
        self.running = False

    def reset_timer(self):
        self.time = 0

    def start_timer(self, inst=None):
        self.time_started = time()
        self.running = True
        GLib.timeout_add(33, self.update_timer)

    def update_timer(self, inst=None):

        if not self.running:
            return False

        self.time = (time() - self.time_started) // 1000

        # max time 99:59:999
        if self.time < MAX_TIME:
            self.emit("update")
        else:
            self.stop_timer()
            return False

        return True

    def stop_timer(self, inst=None):
        if self.running:
            self.running = False
            self.time = min((time() - self.time_started) // 1000, MAX_TIME)
            self.emit("stop")

