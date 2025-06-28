from gi.repository import Gtk, Adw
import gi

from src.backend.PluginManager import PluginBase

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

APPLICATION_1 = "Application 1"
APPLICATION_2 = "Application 2"
APPLICATION_3 = "Application 3"
APPLICATION_4 = "Application 4"


class PluginSettings:
    _application_1: Adw.EntryRow
    _application_2: Adw.EntryRow
    _application_3: Adw.EntryRow
    _application_4: Adw.EntryRow

    def __init__(self, plugin_base: PluginBase):
        self._plugin_base = plugin_base

    def get_settings_area(self) -> Adw.PreferencesGroup:

        self._application_1 = Adw.EntryRow(
            title=self._plugin_base.lm.get("actions.base.APPLICATION_1"))

        self._application_2 = Adw.EntryRow(
            title=self._plugin_base.lm.get("actions.base.APPLICATION_2"))

        self._application_3 = Adw.EntryRow(
            title=self._plugin_base.lm.get("actions.base.APPLICATION_3"))

        self._application_4 = Adw.EntryRow(
            title=self._plugin_base.lm.get("actions.base.APPLICATION_4"))


        self._application_1.connect(
            "notify::text", self._on_change_application_1)

        self._application_2.connect(
            "notify::text", self._on_change_application_2)

        self._application_3.connect(
            "notify::text", self._on_change_application_3)

        self._application_4.connect(
            "notify::text", self._on_change_application_4)

        self._load_settings()

        pref_group = Adw.PreferencesGroup()
        pref_group.set_title(self._plugin_base.lm.get(
            "actions.base.settings.title"))
        pref_group.add(self._application_1)
        pref_group.add(self._application_2)
        pref_group.add(self._application_3)
        pref_group.add(self._application_4)
        return pref_group

    def _load_settings(self):
        settings = self._plugin_base.get_settings()
        application_1 = settings.get(APPLICATION_1, "")
        application_2 = settings.get(APPLICATION_2, "")
        application_3 = settings.get(APPLICATION_3, "")
        application_4 = settings.get(APPLICATION_4, "")

        self._application_1.set_text(application_1)
        self._application_2.set_text(application_2)
        self._application_3.set_text(application_3)
        self._application_4.set_text(application_4)

    def _update_settings(self, key: str, value: str):
        settings = self._plugin_base.get_settings()
        settings[key] = value
        self._plugin_base.set_settings(settings)

    def _on_change_application_1(self, entry, _):
        val = entry.get_text().strip()
        self._update_settings(APPLICATION_1, val)

    def _on_change_application_2(self, entry, _):
        val = entry.get_text().strip()
        self._update_settings(APPLICATION_2, val)

    def _on_change_application_3(self, entry, _):
        val = entry.get_text().strip()
        self._update_settings(APPLICATION_3, val)

    def _on_change_application_4(self, entry, _):
        val = entry.get_text().strip()
        self._update_settings(APPLICATION_4, val)

