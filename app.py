import avango
import avango.script
import avango.gua
import avango.gua.gui
import sys

from compression.compression_configurator import LibpccCompressionConfigurator, RgbdCompressionConfigurator 
from compression.compression_text import CompressionText
from compression.compression_gui import CompressionGui

from input.timed_rotate import TimedRotate

SPOINTS_CONFIG = ""
VIDEO3D_CONFIG = ""
LIBPCC_COMPRESSION_CONFIGURATOR = None
RGBD_COMPRESSION_CONFIGURATOR = None
COMPRESSION_GUI = CompressionGui()
#KEYBOARD_DEVICE_NUM = 0
KEYBOARD_DEVICE_NUM = 1
#KEYBOARD_DEVICE_NUM = 2
#KEYBOARD_DEVICE_NUM = 3
AVATAR_PARENT = None
SPOINTS_AVATAR = None
VIDEO3D_AVATAR = None

def _apply_gui_hack(GUI_PARENT):
    ''' helper for setup_gui. 
        if hack isn't applied gui setup somehow crashes app. '''
    global LIBPCC_COMPRESSION_CONFIGURATOR
    hack = CompressionText()
    hack.my_constructor(
        CONFIGURATOR=LIBPCC_COMPRESSION_CONFIGURATOR,
        PARENT_NODE=GUI_PARENT,
        SCALE=0.03
    )
    hack.node.Transform.value = avango.gua.make_trans_mat(0,0.7,0)
    hack.disconnect()
    hack.node.Tags.value = ['invisible']

def _setup_gui(GUI_PARENT):
    ''' helper function for setup_scene 
        to add gui components to scene. '''
    global LIBPCC_COMPRESSION_CONFIGURATOR
    global RGBD_COMPRESSION_CONFIGURATOR
    global COMPRESSION_GUI
    _apply_gui_hack(GUI_PARENT)
    COMPRESSION_GUI.my_constructor(
        LIBPCC_CONFIGURATOR = LIBPCC_COMPRESSION_CONFIGURATOR, 
        RGBD_CONFIGURATOR = RGBD_COMPRESSION_CONFIGURATOR, 
        PARENT_NODE = GUI_PARENT
    )
    COMPRESSION_GUI.Keyboard.set_device_number(KEYBOARD_DEVICE_NUM)
    
def _setup_spoints(SPOINTS_PARENT):
    ''' helper function for setup_scene 
        to add spoints components to scene. '''
    global SPOINTS_CONFIG
    global LIBPCC_COMPRESSION_CONFIGURATOR
    global KEYBOARD_DEVICE_NUM
    global SPOINTS_AVATAR

    spointsloader = avango.gua.nodes.SPointsLoader()
    spoints_geode = spointsloader.load("kinect-spoints", SPOINTS_CONFIG)
    
    LIBPCC_COMPRESSION_CONFIGURATOR = LibpccCompressionConfigurator()
    LIBPCC_COMPRESSION_CONFIGURATOR.Keyboard.set_device_number(KEYBOARD_DEVICE_NUM)
    LIBPCC_COMPRESSION_CONFIGURATOR.set_spoints_geode(spoints_geode)
    LIBPCC_COMPRESSION_CONFIGURATOR.verbose = False
    print(LIBPCC_COMPRESSION_CONFIGURATOR.get_usage_hint())

    SPOINTS_AVATAR = avango.gua.nodes.TransformNode(
        Name="spoints-transform",
        Children=[spoints_geode]
    )
    SPOINTS_AVATAR.Transform.value = \
        avango.gua.make_trans_mat(0.75, -1.57, 0.0) * \
        avango.gua.make_rot_mat(180, 0.0, 1.0, 0.0)

    SPOINTS_PARENT.Children.value.append(SPOINTS_AVATAR)

def _setup_video3d(VIDEO3D_PARENT):
    ''' helper function for setup_scene 
        to add video3d components to scene. '''
    global VIDEO3D_CONFIG
    global RGBD_COMPRESSION_CONFIGURATOR
    global KEYBOARD_DEVICE_NUM
    global VIDEO3D_AVATAR

    videoloader = avango.gua.nodes.Video3DLoader()
    video3d_geode = videoloader.load("kinect-video3d", VIDEO3D_CONFIG)

    RGBD_COMPRESSION_CONFIGURATOR = RgbdCompressionConfigurator()
    RGBD_COMPRESSION_CONFIGURATOR.Keyboard.set_device_number(KEYBOARD_DEVICE_NUM)
    RGBD_COMPRESSION_CONFIGURATOR.set_video3d_geode(video3d_geode)
    RGBD_COMPRESSION_CONFIGURATOR.verbose = False
    print(RGBD_COMPRESSION_CONFIGURATOR.get_usage_hint())
    RGBD_COMPRESSION_CONFIGURATOR.set_enabled(False)

    VIDEO3D_AVATAR = avango.gua.nodes.TransformNode(
        Name="video3d-transform",
        Children=[video3d_geode]
    )
    VIDEO3D_AVATAR.Transform.value = \
        avango.gua.make_trans_mat(-0.75, -1.57, 0.0) * \
        avango.gua.make_rot_mat(180, 0.0, 1.0, 0.0)
    
    VIDEO3D_PARENT.Children.value.append(VIDEO3D_AVATAR)

def setup_scene(graph):
    ''' helper function to setup scene graph '''
    global SPOINTS_CONFIG
    global VIDEO3D_CONFIG
    global COMPRESSION_GUI
    global AVATAR_PARENT

    if len(SPOINTS_CONFIG) == 0:
        print("Failure: please initialize app.SPOINTS_CONFIG.")
        print("  > Exiting.")
        sys.exit()
    if len(VIDEO3D_CONFIG) == 0:
        print("Failure: please initialize app.SPOINTS_CONFIG.")
        print("  > Exiting.")
        sys.exit() 

    AVATAR_PARENT = avango.gua.nodes.TransformNode(Name="avatar-parent")
    AVATAR_PARENT.Transform.value = avango.gua.make_trans_mat(0,0,-2)
    graph.Root.value.Children.value.append(AVATAR_PARENT)

    #print("joooo\n\njoooo\n\njoooo\n\njoooo\n\njoooo\n\njoooo\n\njoooo\n\n")
    _setup_spoints(AVATAR_PARENT)
    _setup_video3d(AVATAR_PARENT)
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