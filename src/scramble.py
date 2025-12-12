from gi.repository import Gtk
from .utils import scramble_gen

number = 20

class Scramble(Gtk.Label):
    __gtype_name__ = 'Scramble'

    def __init__(self, **kargs):
        self.dim = "3x3x3"
        self.scramble = scramble_gen(number, self.dim)
        self.set_text(self.scramble)

    def update_scramble(self, dim=""):
        if len(dim) > 0:
            self.dim = dim

        font_size = {
            "2x2x2": 44,
            "3x3x3": 38,
            "4x4x4": 32,
            "5x5x5": 28,
            "6x6x6": 24,
            "7x7x7": 22,
            "Megaminx": 22,
            "Pyraminx": 40,
            "Skewb": 44
        }
        self.scramble = scramble_gen(number, self.dim)
        self.set_markup(f"<span size='{font_size[self.dim] * 1024}'>{self.scramble}</span>")

    def show_scramble(self):
        self.set_visible(True)

    def hide_scramble(self):
        self.set_visible(False)


if __name__ == "__main__":
    print(scramble_gen(int(input(_("Enter scramble length:- ")))))
