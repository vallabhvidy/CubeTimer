from gi.repository import Gtk, Adw, Gio

settings = Gio.Settings(schema_id="io.github.vallabhvidy.CubeTimer")

@Gtk.Template(resource_path='/io/github/vallabhvidy/CubeTimer/preferences.ui')
class Preferences(Adw.PreferencesDialog):
    __gtype_name__ = "Preferences"

    hold_to_start = Gtk.Template.Child()
    wca_inspection = Gtk.Template.Child()
    stop_timer_any_key = Gtk.Template.Child()
    zen_mode = Gtk.Template.Child()
    show_mins = Gtk.Template.Child()
    precision = Gtk.Template.Child()
    wca_avg = Gtk.Template.Child()

    def __init__(self, **kargs):
        super().__init__(**kargs)

        self.wca_inspection.set_visible(False)

        settings.bind("hold-to-start", self.hold_to_start, "active", Gio.SettingsBindFlags.DEFAULT)
        settings.bind("wca-inspection", self.wca_inspection, "active", Gio.SettingsBindFlags.DEFAULT)
        settings.bind("stop-timer-any-key", self.stop_timer_any_key, "active", Gio.SettingsBindFlags.DEFAULT)
        settings.bind("zen-mode", self.zen_mode, "active", Gio.SettingsBindFlags.DEFAULT)
        settings.bind("show-mins", self.show_mins, "active", Gio.SettingsBindFlags.DEFAULT)
        settings.bind("precision", self.precision, "value", Gio.SettingsBindFlags.DEFAULT)
        settings.bind("wca-avg", self.wca_avg, "active", Gio.SettingsBindFlags.DEFAULT)


