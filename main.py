import avango
import avango.script
import avango.gua
from examples_common.GuaVE import GuaVE
import sys

from avango.script import field_has_changed
   
import app

def start(filename):
    # setup scenegraph
    graph = avango.gua.nodes.SceneGraph(Name="scenegraph")
    app.setup_scene(graph, filename)

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

if __name__ == '__main__':
    start(sys.argv[1])