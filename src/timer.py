from gi.repository import GLib, GObject

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
        GLib.timeout_add(10, self.update_timer)

    def update_timer(self, inst=None):
        self.time = (time() - self.time_started) // 10000
        self.emit("update")
        return self.running

    def stop_timer(self, inst=None):
        self.emit("stop")
        self.running = False

