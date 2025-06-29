from loguru import logger as log

from GtkHelper.GenerativeUI.ExpanderRow import ExpanderRow
from GtkHelper.GenerativeUI.ScaleRow import ScaleRow
from GtkHelper.GenerativeUI.EntryRow import EntryRow
from GtkHelper.ComboRow import SimpleComboRowItem, BaseComboRowItem
from GtkHelper.GenerativeUI.ComboRow import ComboRow
from GtkHelper.GenerativeUI.SwitchRow import SwitchRow
from src.backend.PluginManager.ActionCore import ActionCore
from src.backend.DeckManagement.InputIdentifier import Input
from src.backend.PluginManager.EventAssigner import EventAssigner
from .. import audioUtils
from ..globals import Icons


class AdjustVolume(ActionCore):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.has_configuration = True
        self.Volume = "N/A"
        self.ApplicationName = ""
        self.bounds = "100"
        self.multiplier = "1"
        self.create_generative_ui()

        self.create_event_listener()

    def create_generative_ui(self):

        self.Application_Name = EntryRow(
            action_core=self,
            var_name="application-name",
            default_value="",
            title="Application Name",
            on_change=self.on_application_name_change
        )

        self.volume_multiplier_scale = ScaleRow(
            action_core=self,
            var_name="volume-adjust",
            default_value=1,
            min=1,
            max=100,
            step=1,
            digits=0,
            title="Multiplier",
            draw_value=True,
            on_change=self.on_volume_adjust_change
        )

        self.volume_bound_scale = ScaleRow(
            action_core=self,
            var_name="volume-bounds",
            default_value=100,
            min=0,
            max=150,
            step=1,
            digits=0,
            title="Maximum Audio Bounds",
            draw_value=True,
            on_change=self.on_volume_bound_change
        )

    def get_config_rows(self):
        return [self.Application_Name._widget, self.volume_multiplier_scale._widget, self.volume_bound_scale._widget]

    def create_event_listener(self):
        self.add_event_assigner(EventAssigner(
            id="adjust-volume-positive-axiom",
            ui_label="Adjust Volume Positive",
            default_event=Input.Dial.Events.TURN_CW,
            callback=self.event_adjust_volume_positive
        ))

        self.add_event_assigner(EventAssigner(
            id="adjust-volume-negative-axiom",
            ui_label="Adjust Volume Negative",
            default_event=Input.Dial.Events.TURN_CCW,
            callback=self.event_adjust_volume_negative
        ))

    def event_adjust_volume_positive(self, event):
        self.adjust_volume(1)

    def event_adjust_volume_negative(self, event):
        self.adjust_volume(-1)

    def on_application_name_change(self, widget, value, old):
        self.ApplicationName = value

    def on_volume_adjust_change(self, widget, value, old):
        self.multiplier = value

    def on_volume_bound_change(self, widget, value, old):
        self.bounds = value

    def adjust_volume(self, modifier):
        try:
            applicationIDs = audioUtils.GetNodeID(self.ApplicationName)

            audioLevel = audioUtils.GetVolume(applicationIDs)
            Volume = self.limit_to_bounds(
                int(self.multiplier) * modifier + audioLevel)
            audioUtils.SetVolume(
                applicationIDs, Volume)
            self.Volume = audioLevel
            self.on_update()
            return

        except Exception as e:
            log.error(e)
            self.show_error(1)

    def dispaly_volume(self):
        if not self.Volume:
            return

        self.set_center_label(str(self.Volume))

    def on_update(self):
        self.dispaly_volume()
        # self.display_icon()
        return

    def on_tick(self):
        if len(self.ApplicationName) > 0:
            applicationIDs = audioUtils.GetNodeID(self.ApplicationName)
            tempVol = audioUtils.GetVolume(applicationIDs)
            if self.Volume == "N/A" or tempVol != int(self.Volume):
                self.Volume = tempVol
        self.dispaly_volume()
        # self.display_icon()
        return

    def on_ready(self):
        self.on_update()

    def limit_to_bounds(self, volume) -> int:
        if volume < 0:
            return 0
        elif volume > int(self.bounds):
            return int(self.bounds)
        return volume
