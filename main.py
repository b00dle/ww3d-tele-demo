import avango
import avango.script
import avango.gua
from examples_common.GuaVE import GuaVE
import sys

from avango.script import field_has_changed

from input.Device import KeyboardDevice

def set_grid_dimensions(spoints_geode, dim):
    if len(dim) == 3:
        spoints_geode.GlobalGridDimensionX.value = dim[0]
        spoints_geode.GlobalGridDimensionY.value = dim[1]
        spoints_geode.GlobalGridDimensionZ.value = dim[2]

def set_point_precision(spoints_geode, prec):
    if len(prec) == 3:
        spoints_geode.GlobalPointPrecisionX.value = prec[0]
        spoints_geode.GlobalPointPrecisionY.value = prec[1]
        spoints_geode.GlobalPointPrecisionZ.value = prec[2]

class CompressionConfigurator(avango.script.Script):
    Keyboard = KeyboardDevice()
    ReduceGridDimensons = avango.SFBool()
    IncreaseGridDimensons = avango.SFBool()
    ReducePointPrecision = avango.SFBool()
    IncreasePointPrecision = avango.SFBool()

    def __init__(self):
        self.super(CompressionConfigurator).__init__()
        self.always_evaluate(True)
        self.settings = {
            "point_precision" : [4,4,4],
            "grid_dimension" : [2,2,2]
        }
        self.spoints_geode = None
        self.ReduceGridDimensons.value = False
        self.IncreaseGridDimensons.value = False
        self.ReducePointPrecision.value = False
        self.IncreasePointPrecision.value = False
        self.verbose = True
        
    def set_spoints_geode(self, node):
        self.spoints_geode = node
        if self.spoints_geode is not None:
            self.update_spoints_geode()

    @field_has_changed(ReducePointPrecision)
    def reduce_point_precision(self):
        if self.ReducePointPrecision.value:
            if min(self.settings["point_precision"]) > 1:
                self.settings["point_precision"] = [p-1 for p in self.settings["point_precision"]]
                self.update_spoints_geode()

    @field_has_changed(IncreasePointPrecision)
    def increase_point_precision(self):
        if self.IncreasePointPrecision.value:
            if max(self.settings["point_precision"]) < 32:
                self.settings["point_precision"] = [p+1 for p in self.settings["point_precision"]]
                self.update_spoints_geode()

    @field_has_changed(ReduceGridDimensons)
    def reduce_grid_dimensions(self):
        if self.ReduceGridDimensons.value:
            if min(self.settings["grid_dimension"]) > 1:
                self.settings["grid_dimension"] = [g-1 for g in self.settings["grid_dimension"]]
                self.update_spoints_geode()

    @field_has_changed(IncreaseGridDimensons)
    def increase_grid_dimensions(self):
        if self.IncreaseGridDimensons.value:
            if max(self.settings["grid_dimension"]) < 16:
                self.settings["grid_dimension"] = [g+1 for g in self.settings["grid_dimension"]]
                self.update_spoints_geode()
    
    def evaluate(self):
        # process changes in point precision
        if self.Keyboard.KeyA.value and not self.ReducePointPrecision.value:
            self.ReducePointPrecision.value = True
        elif not self.Keyboard.KeyA.value and self.ReducePointPrecision.value:
            self.ReducePointPrecision.value = False
        elif self.Keyboard.KeyD.value and not self.IncreasePointPrecision.value:
            self.IncreasePointPrecision.value = True
        elif not self.Keyboard.KeyD.value and self.IncreasePointPrecision.value:
            self.IncreasePointPrecision.value = False
        # process changes in grid precision
        if self.Keyboard.KeyLeft.value and not self.ReduceGridDimensons.value:
            self.ReduceGridDimensons.value = True
        elif not self.Keyboard.KeyLeft.value and self.ReduceGridDimensons.value:
            self.ReduceGridDimensons.value = False
        elif self.Keyboard.KeyRight.value and not self.IncreaseGridDimensons.value:
            self.IncreaseGridDimensons.value = True
        elif not self.Keyboard.KeyRight.value and self.IncreaseGridDimensons.value:
            self.IncreaseGridDimensons.value = False
        
    def update_spoints_geode(self):
        set_grid_dimensions(self.spoints_geode, self.settings["grid_dimension"]) 
        set_point_precision(self.spoints_geode, self.settings["point_precision"])
        if self.verbose:
            print(self.settings)
        

class TimedRotate(avango.script.Script):
    TimeIn = avango.SFFloat()
    MatrixOut = avango.gua.SFMatrix4()

    def evaluate(self):
        self.MatrixOut.value = avango.gua.make_trans_mat(
            0.0, -1.0, -2.0) * avango.gua.make_rot_mat(10 * self.TimeIn.value *
                                                       2.0, 0.0, 1.0, 0.0)

def start(filename):
    # setup scenegraph
    graph = avango.gua.nodes.SceneGraph(Name="scenegraph")
    loader = avango.gua.nodes.TriMeshLoader()

    spointsloader = avango.gua.nodes.SPointsLoader()
    spoints_geode = spointsloader.load("kinect", filename)

    configurator = CompressionConfigurator()
    configurator.Keyboard.set_device_number(1)
    configurator.set_spoints_geode(spoints_geode)

    transform1 = avango.gua.nodes.TransformNode(Children=[spoints_geode])

    light = avango.gua.nodes.LightNode(
        Type=avango.gua.LightType.POINT,
        Name="light",
        Color=avango.gua.Color(1.0, 1.0, 1.0),
        Brightness=100.0,
        Transform=(avango.gua.make_trans_mat(1, 1, 5) *
                   avango.gua.make_scale_mat(30, 30, 30)))

    size = avango.gua.Vec2ui(1024, 768)

    window = avango.gua.nodes.GlfwWindow(Size=size, LeftResolution=size)

    avango.gua.register_window("window", window)

    cam = avango.gua.nodes.CameraNode(
        LeftScreenPath="/screen",
        SceneGraph="scenegraph",
        Resolution=size,
        OutputWindowName="window",
        Transform=avango.gua.make_trans_mat(0.0, 0.0, 3.5))

    res_pass = avango.gua.nodes.ResolvePassDescription()
    res_pass.EnableSSAO.value = True
    res_pass.SSAOIntensity.value = 4.0
    res_pass.SSAOFalloff.value = 10.0
    res_pass.SSAORadius.value = 7.0

    #res_pass.EnableScreenSpaceShadow.value = True

    res_pass.EnvironmentLightingColor.value = avango.gua.Color(0.1, 0.1, 0.1)
    res_pass.ToneMappingMode.value = avango.gua.ToneMappingMode.UNCHARTED
    res_pass.Exposure.value = 1.0
    res_pass.BackgroundColor.value = avango.gua.Color(0.45, 0.5, 0.6)

    anti_aliasing = avango.gua.nodes.SSAAPassDescription()

    pipeline_description = avango.gua.nodes.PipelineDescription(
        Passes=[
            avango.gua.nodes.TriMeshPassDescription(),
            avango.gua.nodes.LightVisibilityPassDescription(),
            avango.gua.nodes.SPointsPassDescription(),
            res_pass,
            anti_aliasing,
        ])

    cam.PipelineDescription.value = pipeline_description

    screen = avango.gua.nodes.ScreenNode(
        Name="screen",
        Width=2,
        Height=1.5,
        Children=[cam])

    graph.Root.value.Children.value = [transform1, light, screen]

    #setup viewer
    viewer = avango.gua.nodes.Viewer()
    viewer.SceneGraphs.value = [graph]
    viewer.Windows.value = [window]

    monkey_updater = TimedRotate()

    timer = avango.nodes.TimeSensor()
    monkey_updater.TimeIn.connect_from(timer.Time)

    transform1.Transform.connect_from(monkey_updater.MatrixOut)

    guaVE = GuaVE()
    guaVE.start(locals(), globals())

    viewer.run()


if __name__ == '__main__':
    start(sys.argv[1])
