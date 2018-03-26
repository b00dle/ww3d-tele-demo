# import guacamole libraries
import avango
import avango.gua
import avango.gua.gui
import avango.script

from avango.script import field_has_changed

class CompressionGui(avango.script.Script):
    UpdateText = avango.SFBool()

    def __init__(self):
        self.super(CompressionGui).__init__()

    def my_constructor(self, CONFIGURATOR, PARENT_NODE, SCALE=1.0):
        self.gui_resource = avango.gua.gui.nodes.GuiResourceNode(
            Size=avango.gua.Vec2(320, 180),
            URL="asset://gua/data/html/compression_info.html",
            TextureName="compression_info"
        )

        self.node = avango.gua.nodes.TexturedScreenSpaceQuadNode()
        self.node.Name.value = "gui-geometry"
        self.node.Texture.value = self.gui_resource.TextureName.value
        self.node.Width.value = int(self.gui_resource.Size.value[0]*SCALE)
        self.node.Height.value = int(self.gui_resource.Size.value[1]*SCALE)     
        self.node.Anchor.value = avango.gua.Vec2(1.0, -1.0)

        PARENT_NODE.Children.value.append(self.node)

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
                self.gui_resource.call_javascript("set_grid_dim", [str(v) for v in value])
            elif key == "point_precision":
                self.gui_resource.call_javascript("set_point_prec", [str(v) for v in value])
            elif key == "color_precision":
                self.gui_resource.call_javascript("set_color_prec", [str(v) for v in value])
            else:
                continue

    def connect(self):
        self.UpdateText.connect_from(self.configurator.Updated)

    def disconnect(self):
        self.UpdateText.disconnect_from(self.configurator.Updated)

    def hide(self):
        self.node.Tags.value = ["invisible"]

    def show(self):
        self.node.Tags.value = []