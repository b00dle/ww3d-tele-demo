# import guacamole libraries
import avango
import avango.gua
import avango.gua.gui
import avango.script
import json

from avango.script import field_has_changed

from input.device import KeyboardDevice

class CompressionGui(avango.script.Script):
    Keyboard = KeyboardDevice()
    UpdateText = avango.SFBool()
    ToggleGui = avango.SFBool()
    ToggleVisible = avango.SFBool()

    def __init__(self):
        self.super(CompressionGui).__init__()

    def my_constructor(self, LIBPCC_CONFIGURATOR, RGBD_CONFIGURATOR, PARENT_NODE, SCALE=2.0):
        self.gui_resource = avango.gua.gui.nodes.GuiResourceNode(
            Size=avango.gua.Vec2(320, 500),
            URL="asset://gua/data/html/compression_info.html",
            TextureName="compression_info"
        )

        self.node = avango.gua.nodes.TexturedScreenSpaceQuadNode()
        self.node.Name.value = "gui-geometry"
        self.node.Texture.value = self.gui_resource.TextureName.value
        self.node.Width.value = int(self.gui_resource.Size.value[0]*SCALE)
        self.node.Height.value = int(self.gui_resource.Size.value[1]*SCALE)     
        self.node.Anchor.value = avango.gua.Vec2(-0.85, -0.9)
        #self.node.Anchor.value = avango.gua.Vec2(-0.8, -0.5)

        PARENT_NODE.Children.value.append(self.node)

        self.libpcc_configurator = LIBPCC_CONFIGURATOR
        if self.libpcc_configurator is not None:
            self.libpcc_configurator.set_enabled(True)
            self.UpdateText.connect_from(self.libpcc_configurator.Updated)

        self.rgbd_configurator = RGBD_CONFIGURATOR
        if self.rgbd_configurator is not None:
            self.rgbd_configurator.set_enabled(False)
            self.UpdateText.connect_from(self.rgbd_configurator.Updated)

        self._have_toggled_gui = False
        self.ToggleGui.value = False
        self.ToggleGui.connect_from(self.Keyboard.Key1)

        self._have_toggled_visible = False
        self.ToggleVisible.value = False
        self.ToggleVisible.connect_from(self.Keyboard.Key2)

        self.last_libpcc_appendix = ""
        self.last_rgbd_appendix = ""

        self._update_text()
        self._update_appendix()

        self.always_evaluate(True)

    @field_has_changed(UpdateText)
    def _update_text(self):
        #if not self.UpdateText.value:
        #    return
        if self.libpcc_configurator.is_enabled():
            for key, value in self.libpcc_configurator.get_settings().items():
                if key == "grid_dimension":
                    self.gui_resource.call_javascript("set_grid_dim", [str(v) for v in value])
                elif key == "point_precision":
                    self.gui_resource.call_javascript("set_point_prec", [str(v) for v in value])
                elif key == "color_precision":
                    self.gui_resource.call_javascript("set_color_prec", [str(v) for v in value])
                elif key == "point_size":
                    self.gui_resource.call_javascript("set_point_size", [str(value)])
                else:
                    continue
        elif self.rgbd_configurator is not None and self.rgbd_configurator.is_enabled():
            for key, value in self.rgbd_configurator.get_settings().items():
                if key == "global_comp_lvl":
                    self.gui_resource.call_javascript("set_global_comp", [str(value)])
                elif key == "depth_comp_lvl":
                    self.gui_resource.call_javascript("set_depth_comp", [str(value)])
                elif key == "color_comp_lvl":
                    self.gui_resource.call_javascript("set_color_comp", [str(value)])
                else:
                    continue

    @field_has_changed(ToggleGui)
    def _toggle_ui(self):
        if not self.ToggleGui.value:
            self._have_toggled_gui = False
            return
        elif self._have_toggled_gui:
            return
        if self.libpcc_configurator is not None:
            libpcc_enabled = not self.libpcc_configurator.is_enabled()
            self.libpcc_configurator.set_enabled(libpcc_enabled)
            self.gui_resource.call_javascript("set_libpcc_visible", [str(libpcc_enabled)])
        if self.rgbd_configurator is not None:
            rgbd_enabled = not self.rgbd_configurator.is_enabled()
            self.rgbd_configurator.set_enabled(rgbd_enabled)
            self.gui_resource.call_javascript("set_rgbd_visible", [str(rgbd_enabled)])
        self._have_toggled_gui = True

    @field_has_changed(ToggleVisible)
    def _toggle_visible(self):
        if not self.ToggleVisible.value:
            self._have_toggled_visible = False
            return
        elif self._have_toggled_visible:
            return
        if len(self.node.Tags.value) == 0:
            self.node.Tags.value = ['invisible']
        else:
            self.node.Tags.value = []
        self._have_toggled_visible = True

    def evaluate(self):
        self._update_text()
        self._update_appendix()

    def _update_appendix(self):
        appendix_data = ""
        if self.libpcc_configurator is not None:
            if self.libpcc_configurator.is_enabled():
                if self.libpcc_configurator.spoints_geode:
                    try:
                        appendix_data = self.libpcc_configurator.spoints_geode.MsgAppendix.value
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
                            self.last_libpcc_appendix = appendix_data
                        else:
                            appendix_data = self.last_libpcc_appendix
                    except ValueError as e:
                        print("Error parsing grid message appendix:\n", e)
                        print("  > could not retrieve appendix data")
                        appendix_data = ""
        elif self.rgbd_configurator is not None and self.rgbd_configurator.is_enabled():
            if self.rgbd_configurator.video3d_geode is not None:
                try:
                    appendix_data = self.rgbd_configurator.video3d_geode.DebugMessage.value
                except ValueError as e:
                    print("Error parsing video3d debug message:\n", e)
                if len(appendix_data) > 0:
                    self.last_rgbd_appendix = appendix_data
                else:
                    appendix_data = self.last_rgbd_appendix
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
        self.UpdateText.connect_from(self.libpcc_configurator.Updated)

    def disconnect(self):
        self.UpdateText.disconnect_from(self.libpcc_configurator.Updated)

    def hide(self):
        self.node.Tags.value = ["invisible"]

    def show(self):
        self.node.Tags.value = []