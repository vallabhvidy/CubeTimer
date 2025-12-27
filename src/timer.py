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

    def start_timer(self):
        self.time_started = time()
        self.running = True
        GLib.timeout_add(1, self.update_timer)

    def update_timer(self):
        self.time = (time() - self.time_started) // 1000
        # max time 99:59:999
        if self.time < (99 * 60000 + 59 * 1000 + 999):
            self.emit("update")
        else:
            self.stop_timer()
            self.emit("stop")
        if not self.running:
            self.emit("stop")
        return self.running

    def stop_timer(self):
        self.running = False

