from gi.repository import Gtk
from .utils import scramble_gen

number = 20

scramble_font_size = {
    "2x2x2": 44,
    "3x3x3": 38,
    "4x4x4": 32,
    "5x5x5": 28,
    "6x6x6": 22,
    "7x7x7": 18,
    "Megaminx": 20,
    "Pyraminx": 40,
    "Skewb": 44,
    "Clock": 32
}

class Scramble(Gtk.Label):
    __gtype_name__ = 'Scramble'

    def __init__(self, **kargs):
        self.dim = "3x3x3"
        self.scale_factor = 1
        self.update_scramble()

    def update_scramble(self, dim=None):
        if dim:
            self.dim = dim

        self.scramble = scramble_gen(number, self.dim)
        self.update_label()

    def update_label(self):
        self.set_markup(f"<span size='{
            int(scramble_font_size[self.dim] * self.scale_factor)
        }pt'>{self.scramble}</span>")

    def show_scramble(self):
        self.set_visible(True)

    def hide_scramble(self):
        self.set_visible(False)


if __name__ == "__main__":
    print(scramble_gen(int(input(_("Enter scramble length:- ")))))
