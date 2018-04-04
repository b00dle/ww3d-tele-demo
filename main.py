import avango
import avango.script
import avango.gua
from examples_common.GuaVE import GuaVE
import sys

from avango.script import field_has_changed
   
import app
from viewing.ViewingSetup import StereoViewingSetup

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

    print_graph(graph.Root.value)

    size = avango.gua.Vec2ui(1024, 768)
    viewingSetup = StereoViewingSetup(
        SCENEGRAPH = graph,
        WINDOW_RESOLUTION = size,
        SCREEN_DIMENSIONS = avango.gua.Vec2(1.0, 768/1024),
        LEFT_SCREEN_RESOLUTION = size,
        RIGHT_SCREEN_RESOLUTION = size
    )
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