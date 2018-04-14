import avango
import avango.script
import avango.gua
from examples_common.GuaVE import GuaVE
import sys

from avango.script import field_has_changed
   
import app
from viewing.ViewingSetup import StereoViewingSetup
from input.device import SpaceMouseMove, SpaceMouseRotate

def start():
    # setup scenegraph
    graph = avango.gua.nodes.SceneGraph(Name="scenegraph")
    app.setup_scene(graph)

    '''
    # window and screen setup
    size = avango.gua.Vec2ui(1024, 768)
    window = avango.gua.nodes.GlfwWindow(Size=size, LeftResolution=size)
    avango.gua.register_window("window", window)
    graph.Root.value.Children.value.append(app.setup_screen(window))

    # viewer setup
    viewer = avango.gua.nodes.Viewer()
    viewer.SceneGraphs.value = [graph]
    viewer.Windows.value = [window]

    guaVE = GuaVE()
    guaVE.start(locals(), globals())

    viewer.run()
    '''
    ## init viewing and interaction setups
    hostname = open('/etc/hostname', 'r').readline()
    hostname = hostname.strip(" \n")

    print("WORKSTATION:", hostname)

    viewingSetup = None

    if hostname == "athena": # small powerwall workstation
        _tracking_transmitter_offset = avango.gua.make_trans_mat(0.0,-1.42,1.6) # transformation into tracking coordinate system

        viewingSetup = StereoViewingSetup(
            SCENEGRAPH = graph,
            WINDOW_RESOLUTION = avango.gua.Vec2ui(1920*2, 1200),
            SCREEN_DIMENSIONS = avango.gua.Vec2(3.0, 2.0),
            LEFT_SCREEN_POSITION = avango.gua.Vec2ui(130, 13),
            LEFT_SCREEN_RESOLUTION = avango.gua.Vec2ui(1780, 1185),
            RIGHT_SCREEN_POSITION = avango.gua.Vec2ui(1925, 13),
            RIGHT_SCREEN_RESOLUTION = avango.gua.Vec2ui(1780, 1185),
            STEREO_FLAG = True,
            STEREO_MODE = avango.gua.StereoMode.SIDE_BY_SIDE,
            HEADTRACKING_FLAG = True,
            HEADTRACKING_STATION = "tracking-glasses-2", # wired 3D-TV glasses on Samsung 3D-TV workstation
            TRACKING_TRANSMITTER_OFFSET = _tracking_transmitter_offset,
            )
        '''
        pointerInput = PointerInput()
        pointerInput.init_art_pointer(
            POINTER_DEVICE_STATION = "device-pointer-2", # Gyromouse
            POINTER_TRACKING_STATION = "tracking-pointer-2", # Gyromouse
            TRACKING_TRANSMITTER_OFFSET = _tracking_transmitter_offset,
            KEYBOARD_STATION = "gua-device-keyboard",
        )
            
        manipulationManager = ManipulationManager()
        manipulationManager.my_constructor(
            SCENEGRAPH = graph,
            NAVIGATION_NODE = viewingSetup.navigation_node,
            HEAD_NODE = viewingSetup.head_node,
            POINTER_INPUT = pointerInput,
            )
        '''
    elif hostname == "artemis": # Samsung 3D-TV workstation
        _tracking_transmitter_offset = avango.gua.make_trans_mat(0.0, -1.3, 1.45) # transformation into tracking coordinate system 

        viewingSetup = StereoViewingSetup(
            SCENEGRAPH = graph,
            WINDOW_RESOLUTION = avango.gua.Vec2ui(1920, 1080),
            SCREEN_DIMENSIONS = avango.gua.Vec2(1.24, 0.69),
            LEFT_SCREEN_RESOLUTION = avango.gua.Vec2ui(1920, 1080),
            RIGHT_SCREEN_RESOLUTION = avango.gua.Vec2ui(1920, 1080),
            STEREO_FLAG = True,
            STEREO_MODE = avango.gua.StereoMode.CHECKERBOARD,
            HEADTRACKING_FLAG = True,
            HEADTRACKING_STATION = "tracking-glasses-3", # wired 3D-TV glasses on Mitsubishi 3D-TV workstation
            TRACKING_TRANSMITTER_OFFSET = _tracking_transmitter_offset,
            )
        '''
        pointerInput = PointerInput()
        pointerInput.init_art_pointer(
            POINTER_DEVICE_STATION = "device-pointer-3", # 2.4G Mouse
            POINTER_TRACKING_STATION = "tracking-pointer-3", # 2.4G Mouse
            TRACKING_TRANSMITTER_OFFSET = _tracking_transmitter_offset,
            KEYBOARD_STATION = "gua-device-keyboard",
        )
            
        manipulationManager = ManipulationManager()
        manipulationManager.my_constructor(
            SCENEGRAPH = graph,
            NAVIGATION_NODE = viewingSetup.navigation_node,
            HEAD_NODE = viewingSetup.head_node,
            POINTER_INPUT = pointerInput,
            )
        '''            
    else:
        size = avango.gua.Vec2ui(1024, 768)
        viewingSetup = StereoViewingSetup(
            SCENEGRAPH = graph,
            WINDOW_RESOLUTION = size,
            SCREEN_DIMENSIONS = avango.gua.Vec2(1.0, 768/1024),
            LEFT_SCREEN_RESOLUTION = size,
            RIGHT_SCREEN_RESOLUTION = size
        )

    move = SpaceMouseMove()
    move.MatrixOut.value = app.AVATAR_PARENT.Transform.value 
    app.AVATAR_PARENT.Transform.connect_from(move.MatrixOut)

    spoints_rotate = SpaceMouseRotate()
    spoints_rotate.MatrixOut.value = app.SPOINTS_AVATAR.Transform.value
    app.SPOINTS_AVATAR.Transform.connect_from(spoints_rotate.MatrixOut) 
    
    video3d_rotate = SpaceMouseRotate()
    video3d_rotate.MatrixOut.value = app.VIDEO3D_AVATAR.Transform.value
    app.VIDEO3D_AVATAR.Transform.connect_from(video3d_rotate.MatrixOut)    

    print("SCENEGRAPH") 
    print_graph(graph.Root.value)
    viewingSetup.run(locals(), globals())

## print the subgraph under a given node to the console
def print_graph(root_node):
  stack = [(root_node, 0)]
  while stack:
    node, level = stack.pop()
    print("│   " * level + "├── {0} <{1}>".format(
      node.Name.value, node.__class__.__name__))
    stack.extend(
      [(child, level + 1) for child in reversed(node.Children.value)])

if __name__ == '__main__':
    if len(sys.argv) < 3:
        app.SPOINTS_CONFIG = "spoints_resource_file.sr"
        app.VIDEO3D_CONFIG = "surface_23_24_25_26_pan_l.ks"
        print("NOTIFICATION: attempting to set default config for SPOINTS and VIDEO3D.")
        print("  > SPOINTS: " + app.SPOINTS_CONFIG)
        print("  > VIDEO3D: " + app.VIDEO3D_CONFIG)
    else:
        app.SPOINTS_CONFIG = sys.argv[1]
        app.VIDEO3D_CONFIG = sys.argv[2]

    sp_conf = ""
    with open(app.SPOINTS_CONFIG, 'r') as content_file:
        sp_conf = content_file.read()

    v3d_conf = ""
    with open(app.VIDEO3D_CONFIG, 'r') as content_file:
        v3d_conf = content_file.read()

    print("=========== SPOINTS_CONFIG ===========")
    print(sp_conf)
    print("======================================")

    print("=========== VIDEO3D_CONFIG ===========")
    print(v3d_conf)
    print("======================================")

    start()