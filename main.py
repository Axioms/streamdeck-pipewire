# Import StreamController modules
import os.path

import pulsectl
from gi.repository import Gtk

from src.backend.PluginManager.PluginBase import PluginBase
from src.backend.PluginManager.ActionHolder import ActionHolder
from src.backend.DeckManagement.ImageHelpers import image2pixbuf

# Import actions
from .actions.SimpleAction.SimpleAction import SimpleAction
from .globals import Icons, Colors
from .settings import PluginSettings


class PluginTemplate(PluginBase):
    def __init__(self):
        super().__init__(use_legacy_locale=False)
        self.init_vars()
        self.lm = self.locale_manager
        self.lm.set_to_os_default()
        self._settings_manager = PluginSettings(self)
        self.has_plugin_settings = True
        # Register actions
        self.simple_action_holder = ActionHolder(
            plugin_base=self,
            action_base=SimpleAction,
            # Change this to your own plugin id
            action_id="dev_core447_Template::SimpleAction",
            action_name="Simple Action",
        )
        self.add_action_holder(self.simple_action_holder)

        # Register plugin
        self.register(
            plugin_name="Template",
            github_repo="https://github.com/StreamController/PluginTemplate",
            plugin_version="1.0.0",
            app_version="1.1.1-alpha"
        )

    def init_vars(self):
        self.add_color(Colors.NORMAL, (0, 0, 0, 0))
        self.add_color(Colors.MUTE, (111, 29, 29, 255))

        size = 0.7
        self.add_icon(Icons.Icon_1, self.get_asset_path("info.png"))
        self.add_icon(Icons.Icon_2, self.get_asset_path("info.png"))
        self.add_icon(Icons.Icon_3, self.get_asset_path("info.png"))
        self.add_icon(Icons.Icon_4, self.get_asset_path("info.png"))
        
    def get_settings_area(self):
        return self._settings_manager.get_settings_area()
