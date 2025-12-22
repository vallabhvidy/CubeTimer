from gi.repository import Gtk, Gdk, Adw

from .utils import time_string, zero_time

@Gtk.Template(resource_path='/io/github/vallabhvidy/CubeTimer/timerlabel.ui')
class CubeTimerLabel(Gtk.Label):
    __gtype_name__ = 'CubeTimerLabel'

    def __init__(self, **kwargs):
        super().__init__(**kwargs, focusable = True, can_focus = True)

        self.time = 0

        # dark mode
        style_manager = Adw.StyleManager.get_default()
        style_manager.connect("notify::dark", self.set_theme)
        self.set_theme(style_manager)

    def set_theme(self, style_manager, pspec=None):
        self.color = "white" if style_manager.get_dark() else "black"
        self.set_colored_label()

    def set_colored_label(self, time=None, color=None):
        """
        update label to give time and color.

        if time is not passed it remains unchanged.

        if  color is not passed it changes to default color
        set by theme.
        """
        color = self.color if color == None else color
        self.time = time if time is not None else self.time
        time = time_string(self.time)
        time = time if time != "DNF" else zero_time()
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
