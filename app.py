import avango
import avango.script
import avango.gua

from compression.compression_configurator import CompressionConfigurator 
from compression.compression_text import CompressionText
from input.timed_rotate import TimedRotate

COMPRESSION_CONFIGURATOR = None
DEBUG_TEXT = CompressionText()

def setup_scene(graph, kinect_config):
    ''' helper function to setup scene graph '''
    global COMPRESSION_CONFIGURATOR

    spointsloader = avango.gua.nodes.SPointsLoader()
    spoints_geode = spointsloader.load("kinect", kinect_config)

    COMPRESSION_CONFIGURATOR = CompressionConfigurator()
    COMPRESSION_CONFIGURATOR.Keyboard.set_device_number(1)
    COMPRESSION_CONFIGURATOR.set_spoints_geode(spoints_geode)
    COMPRESSION_CONFIGURATOR.verbose = False
    print(COMPRESSION_CONFIGURATOR.get_usage_hint())

    timer = avango.nodes.TimeSensor()
    rotation_updater = TimedRotate()
    rotation_updater.TimeIn.connect_from(timer.Time)
    transform1 = avango.gua.nodes.TransformNode(Children=[spoints_geode])
    transform1.Transform.connect_from(rotation_updater.MatrixOut)

    light = avango.gua.nodes.LightNode(
        Type=avango.gua.LightType.POINT,
        Name="light",
        Color=avango.gua.Color(1.0, 1.0, 1.0),
        Brightness=100.0,
        Transform=(avango.gua.make_trans_mat(1, 1, 5) *
                   avango.gua.make_scale_mat(30, 30, 30)))

    DEBUG_TEXT.my_constructor(
        CONFIGURATOR=COMPRESSION_CONFIGURATOR,
        PARENT_NODE=graph.Root.value,
        SCALE=0.03
    )
    DEBUG_TEXT.node.Transform.value = avango.gua.make_trans_mat(0,0.7,0)

    graph.Root.value.Children.value.append(transform1)
    graph.Root.value.Children.value.append(light)

def setup_pipeline():
    ''' helper function to configure pipeline and rendering effects. '''
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
    return pipeline_description

def setup_screen(window):
    ''' helper function to setup viewing parameters. '''  
    cam = avango.gua.nodes.CameraNode(
        LeftScreenPath="/screen",
        SceneGraph="scenegraph",
        Resolution=window.Size.value,
        OutputWindowName="window",
        Transform=avango.gua.make_trans_mat(0.0, 0.0, 3.5))

    cam.PipelineDescription.value = setup_pipeline()

    screen = avango.gua.nodes.ScreenNode(
        Name="screen",
        Width=2,
        Height=1.5,
        Children=[cam])
    return screen