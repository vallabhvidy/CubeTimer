from gi.repository import Gtk, Gdk, Adw

from .timer import CubeTimer
from .utils import time_string

@Gtk.Template(resource_path='/io/github/vallabhvidy/CubeTimer/timerlabel.ui')
class CubeTimerLabel(Gtk.Label):
    __gtype_name__ = 'CubeTimerLabel'

    timer = CubeTimer(lambda: None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs, focusable = True, can_focus = True)

        style_manager = Adw.StyleManager.get_default()
        style_manager.connect("notify::dark", self.set_color)
        self.set_color(style_manager)

        self.timer.update_label = self.set_colored_label

    def set_color(self, style_manager, pspec=None):
        self.color = "white" if style_manager.get_dark() else "black"
        self.set_colored_label()

    def set_colored_label(self, color=None):
        color = self.color if color == None else color
        time = time_string(self.timer.time)
        time = time if time != "DNF" else "00:00.00"
        time_format = _("<span color='{color}'>{time}</span>")
        self.set_markup(time_format.format(
            color=color,
            time=time
        ))

    def make_adaptive(self, size):
        # Size is one of 0, 1

        if size == 0:
            pass
        elif size == 1:
            pass
        else:
            raise Exception("Size is out of range")
