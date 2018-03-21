# import guacamole libraries
import avango
import avango.gua
import avango.script

from avango.script import field_has_changed

from misc.text import Text

class CompressionText(Text):
    UpdateText = avango.SFBool()

    def __init__(self):
        self.super(CompressionText).__init__()

    def my_constructor(self, CONFIGURATOR, PARENT_NODE, SCALE=0.3):
        self.super(CompressionText).my_constructor(PARENT_NODE, "", SCALE)

        self.configurator = CONFIGURATOR
        self.UpdateText.connect_from(self.configurator.Updated)
        self._update_text()

    @field_has_changed(UpdateText)
    def _update_text(self):
        if not self.UpdateText.value:
            return
        dt_str = ""
        for key, value in self.configurator.get_settings().items():
            if key == "grid_dimension":
                dt_str += "G "
            elif key == "point_precision":
                dt_str += "P "
            elif key == "color_precision":
                dt_str += "C "
            else:
                continue
            dt_str += "".join(str(value).split()) + " "
        self.set_text(dt_str)