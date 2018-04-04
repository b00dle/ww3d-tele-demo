import avango
import avango.script
import avango.gua
import avango.gua.gui
import sys

from compression.compression_configurator import CompressionConfigurator 
from compression.compression_text import CompressionText
from compression.compression_gui import CompressionGui

from input.timed_rotate import TimedRotate

SPOINTS_CONFIG = ""
VIDEO3D_CONFIG = ""
COMPRESSION_CONFIGURATOR = None
COMPRESSION_GUI = CompressionGui()

def _apply_gui_hack(GUI_PARENT):
    ''' helper for setup_gui. 
        if hack isn't applied gui setup somehow crashes app. '''
    global COMPRESSION_CONFIGURATOR
    hack = CompressionText()
    hack.my_constructor(
        CONFIGURATOR=COMPRESSION_CONFIGURATOR,
        PARENT_NODE=GUI_PARENT,
        SCALE=0.03
    )
    hack.node.Transform.value = avango.gua.make_trans_mat(0,0.7,0)
    hack.disconnect()
    hack.node.Tags.value = ['invisible']

def _setup_gui(GUI_PARENT):
    ''' helper function for setup_scene 
        to add gui components to scene. '''
    global COMPRESSION_CONFIGURATOR
    global COMPRESSION_GUI
    _apply_gui_hack(GUI_PARENT)
    COMPRESSION_GUI.my_constructor(COMPRESSION_CONFIGURATOR, GUI_PARENT)
    
def _setup_spoints(SPOINTS_PARENT):
    ''' helper function for setup_scene 
        to add spoints components to scene. '''
    global SPOINTS_CONFIG
    global COMPRESSION_CONFIGURATOR
    
    spointsloader = avango.gua.nodes.SPointsLoader()
    spoints_geode = spointsloader.load("kinect-spoints", SPOINTS_CONFIG)

    COMPRESSION_CONFIGURATOR = CompressionConfigurator()
    COMPRESSION_CONFIGURATOR.Keyboard.set_device_number(1)
    #COMPRESSION_CONFIGURATOR.Keyboard.set_device_number(0)
    COMPRESSION_CONFIGURATOR.set_spoints_geode(spoints_geode)
    COMPRESSION_CONFIGURATOR.verbose = False
    print(COMPRESSION_CONFIGURATOR.get_usage_hint())

    spoints_transform = avango.gua.nodes.TransformNode(
        Name="spoints-transform",
        Children=[spoints_geode]
    )
    spoints_transform.Transform.value = \
        avango.gua.make_trans_mat(0.75, -1.0, -2.0) * \
        avango.gua.make_rot_mat(180, 0.0, 1.0, 0.0)
    
    SPOINTS_PARENT.Children.value.append(spoints_transform)

def _setup_video3d(VIDEO3D_PARENT):
    ''' helper function for setup_scene 
        to add video3d components to scene. '''
    global VIDEO3D_CONFIG

    videoloader = avango.gua.nodes.Video3DLoader()
    video_geode = videoloader.load("kinect-video3d", VIDEO3D_CONFIG)

    
    video_transform = avango.gua.nodes.TransformNode(
        Name="video3d-transform",
        Children=[video_geode]
    )
    video_transform.Transform.value = \
        avango.gua.make_trans_mat(-0.75, -1.0, -2.0) * \
        avango.gua.make_rot_mat(180, 0.0, 1.0, 0.0)
    
    VIDEO3D_PARENT.Children.value.append(video_transform)

def setup_scene(graph):
    ''' helper function to setup scene graph '''
    global SPOINTS_CONFIG
    global VIDEO3D_CONFIG
    global COMPRESSION_GUI

    if len(SPOINTS_CONFIG) == 0:
        print("Failure: please initialize app.SPOINTS_CONFIG.")
        print("  > Exiting.")
        sys.exit()
    if len(VIDEO3D_CONFIG) == 0:
        print("Failure: please initialize app.SPOINTS_CONFIG.")
        print("  > Exiting.")
        sys.exit() 

    #_setup_video3d(graph.Root.value)
    _setup_spoints(graph.Root.value)
    _setup_gui(graph.Root.value)

    #COMPRESSION_GUI.hide()

    light = avango.gua.nodes.LightNode(
        Type=avango.gua.LightType.POINT,
        Name="light",
        Color=avango.gua.Color(1.0, 1.0, 1.0),
        Brightness=100.0,
        Transform=(avango.gua.make_trans_mat(1, 1, 5) *
                   avango.gua.make_scale_mat(30, 30, 30)))

    
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
            avango.gua.nodes.Video3DPassDescription(),
            res_pass,
            avango.gua.nodes.TexturedScreenSpaceQuadPassDescription(),
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
    cam.BlackList.value = ["invisible"]

    cam.PipelineDescription.value = setup_pipeline()

    screen = avango.gua.nodes.ScreenNode(
        Name="screen",
        Width=2,
        Height=1.5,
        Children=[cam])
    return screen