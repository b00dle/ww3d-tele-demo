# import guacamole libraries
import avango
import avango.gua
import avango.gua.gui
import avango.script
import json

from avango.script import field_has_changed

class CompressionGui(avango.script.Script):
    UpdateText = avango.SFBool()

    def __init__(self):
        self.super(CompressionGui).__init__()

    def my_constructor(self, CONFIGURATOR, PARENT_NODE, SCALE=1.0):
        self.gui_resource = avango.gua.gui.nodes.GuiResourceNode(
            Size=avango.gua.Vec2(320, 400),
            URL="asset://gua/data/html/compression_info.html",
            TextureName="compression_info"
        )

        self.node = avango.gua.nodes.TexturedScreenSpaceQuadNode()
        self.node.Name.value = "gui-geometry"
        self.node.Texture.value = self.gui_resource.TextureName.value
        self.node.Width.value = int(self.gui_resource.Size.value[0]*SCALE)
        self.node.Height.value = int(self.gui_resource.Size.value[1]*SCALE)     
        self.node.Anchor.value = avango.gua.Vec2(-0.75, 0.5)

        PARENT_NODE.Children.value.append(self.node)

        self.configurator = CONFIGURATOR
        self.UpdateText.connect_from(self.configurator.Updated)
        self._update_text()
        self._update_appendix()

        self.always_evaluate(True)

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

    def evaluate(self):
        self._update_appendix()
    
    def _update_appendix(self):
        appendix_data = ""
        if self.configurator.spoints_geode:
            appendix_data = self.configurator.spoints_geode.MsgAppendix.value
            if appendix_data.startswith("{") and not appendix_data.endswith("}"):
                last_close = 0
                for i in reversed(range(0, len(appendix_data))):
                    if appendix_data[i] == "}":
                        last_close = i
                        break
                if last_close == 0:
                    appendix_data = ""
                else:
                    appendix_data = appendix_data[0:last_close+1]
        if len(appendix_data) > 0:
            is_well_formed = True
            try:
                d = json.loads(appendix_data)
            except ValueError as e:
                print("Error parsing grid message appendix:\n", e)
                print("  > appendix data", appendix_data)
                is_well_formed = False
            finally:
                if is_well_formed:
                    self.gui_resource.call_javascript("update_table_container", [str(appendix_data)])

    def connect(self):
        self.UpdateText.connect_from(self.configurator.Updated)

    def disconnect(self):
        self.UpdateText.disconnect_from(self.configurator.Updated)

    def hide(self):
        self.node.Tags.value = ["invisible"]

    def show(self):
        self.node.Tags.value = []