from gi.repository import Adw, Gtk

from .timerlabel import CubeTimerLabel
from .scramble import Scramble
from .score import ScoresColumnView

scramble_moves = 25

@Gtk.Template(resource_path='/io/github/vallabhvidy/CubeTimer/window.ui')
class CubeTimerWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'CubeTimerWindow'

    cube_timer_label = Gtk.Template.Child()
    header_bar_menu = Gtk.Template.Child()
    scramble = Gtk.Template.Child()
    split_view = Gtk.Template.Child()
    show_sidebar_button = Gtk.Template.Child()
    scores_column_view = Gtk.Template.Child()
    header_bar = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cube_timer_label.grab_focus()
        self.header_bar_menu.set_can_focus(False)
        self.split_view.set_can_focus(False)
        self.header_bar.set_show_title(True)
        evk = Gtk.EventControllerKey.new()
        evk.connect("key-pressed", self.cube_timer_label.timer.key_press)
        evk.connect("key-released", self.cube_timer_label.timer.key_released)
        self.add_controller(evk)
        drop_down = self.header_bar.get_title_widget()
        def on_dropdown_activate(dropdown, pspec):
            selected = dropdown.props.selected_item.get_string()
            self.scramble.update_scramble(selected)
        drop_down.connect("notify::selected-item", on_dropdown_activate)

        self.cube_timer_label.timer.drop_down = drop_down
        self.cube_timer_label.timer.scramble = self.scramble
        self.cube_timer_label.timer.split_view = self.split_view
        self.cube_timer_label.timer.update_scores = self.scores_column_view.add_score
        self.cube_timer_label.timer.sidebar_button = self.show_sidebar_button


