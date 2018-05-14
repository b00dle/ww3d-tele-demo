#!/usr/bin/python

### import guacamole libraries
import avango
import avango.gua
import avango.daemon
import avango.gua.lod
### import application libraries
from examples_common.GuaVE import GuaVE



class User:

    ### class variables ###  
    number_of_instances = 0
    
    ### constructor
    def __init__(self,
        SCENEGRAPH = None,
        NAVIGATION_NODE = None,
        SCREEN_NODE = None,
        DISPLAY_STRING = ":0.0",
        WINDOW_RESOLUTION = avango.gua.Vec2ui(1920, 1200), # default resolution in pixel
        SCREEN_DIMENSIONS = avango.gua.Vec2(4.2, 2.61), # default screen size in meter
        SCREEN_MATRIX = avango.gua.make_identity_mat(),
        HEADTRACKING_SENSOR_STATION = "",
        TRACKING_TRANSMITTER_OFFSET = avango.gua.make_identity_mat(),
        LEFT_POSITION = avango.gua.Vec2ui(0, 0),
        LEFT_RESOLUTION = avango.gua.Vec2ui(1920, 1200),
        RIGHT_POSITION = avango.gua.Vec2ui(1920, 0),
        RIGHT_RESOLUTION = avango.gua.Vec2ui(1920, 1200),
        WARP_MATRIX_RED_RIGHT = "",
        WARP_MATRIX_GREEN_RIGHT = "",
        WARP_MATRIX_BLUE_RIGHT = "",
        WARP_MATRIX_RED_LEFT = "",
        WARP_MATRIX_GREEN_LEFT = "",
        WARP_MATRIX_BLUE_LEFT = "",
        ):

        ## parameter quards
        if SCENEGRAPH is None:
            print("ERROR: scengraph instance missing")            
            quit()
            
        if NAVIGATION_NODE is None:
            print("ERROR: navigation node missing")
            quit()

        if SCREEN_NODE is None:
            print("ERROR: screen node missing")
            quit()

            
        ## @var id
        # Identification number of this User.
        self.id = User.number_of_instances
        User.number_of_instances += 1
        


        ## init window
        self.window = avango.gua.nodes.Window(Title = "window" + str(self.id))
        self.window.Display.value = DISPLAY_STRING
        self.window.EnableVsync.value = False
        #self.window.EnableFullscreen.value = True
        self.window.Size.value = avango.gua.Vec2ui(WINDOW_RESOLUTION.x*2, WINDOW_RESOLUTION.y)
        self.window.StereoMode.value = avango.gua.StereoMode.SIDE_BY_SIDE
        self.window.LeftResolution.value = LEFT_RESOLUTION
        self.window.RightResolution.value = RIGHT_RESOLUTION
        self.window.LeftPosition.value = LEFT_POSITION
        self.window.RightPosition.value = RIGHT_POSITION
        
        avango.gua.register_window(self.window.Title.value, self.window) 


        ## init passes & render pipeline description
        self.resolve_pass = avango.gua.nodes.ResolvePassDescription()
        self.resolve_pass.EnableSSAO.value = True
        self.resolve_pass.SSAOIntensity.value = 3.0
        self.resolve_pass.SSAOFalloff.value = 10.0
        self.resolve_pass.SSAORadius.value = 2.0
        #self.resolve_pass.EnableScreenSpaceShadow.value = True
        self.resolve_pass.EnvironmentLightingColor.value = avango.gua.Color(0.2, 0.2, 0.2)
        self.resolve_pass.ToneMappingMode.value = avango.gua.ToneMappingMode.UNCHARTED
        self.resolve_pass.Exposure.value = 1.0

        #self.resolve_pass.BackgroundMode.value = avango.gua.BackgroundMode.COLOR
        #self.resolve_pass.BackgroundColor.value = avango.gua.Color(0.45, 0.5, 0.6)
        self.resolve_pass.BackgroundMode.value = avango.gua.BackgroundMode.SKYMAP_TEXTURE
        self.resolve_pass.BackgroundTexture.value = "/opt/guacamole/resources/skymaps/HazyDay_01.jpg"
        #self.resolve_pass.BackgroundTexture.value = "/opt/guacamole/resources/skymaps/warehouse.jpg"

        self.pipeline_description = avango.gua.nodes.PipelineDescription(Passes = [])
        self.pipeline_description.EnableABuffer.value = False
        self.pipeline_description.Passes.value.append(avango.gua.nodes.TriMeshPassDescription())
        self.pipeline_description.Passes.value.append(avango.gua.nodes.LineStripPassDescription())
        self.lod_pass = avango.gua.lod.nodes.PLodPassDescription()
        self.lod_pass.SurfelRenderMode.value = avango.gua.lod.RenderFlags.LQ_ONE_PASS
        self.pipeline_description.Passes.value.append(self.lod_pass)
        self.pipeline_description.Passes.value.append(avango.gua.nodes.TexturedQuadPassDescription())
        self.pipeline_description.Passes.value.append(avango.gua.nodes.LightVisibilityPassDescription())
        self.pipeline_description.Passes.value.append(avango.gua.nodes.SPointsPassDescription())
        self.pipeline_description.Passes.value.append(avango.gua.nodes.Video3DPassDescription())
        #self.pipeline_description.Passes.value.append(avango.gua.nodes.BBoxPassDescription())
        self.pipeline_description.Passes.value.append(self.resolve_pass)
        self.pipeline_description.Passes.value.append(avango.gua.nodes.TexturedScreenSpaceQuadPassDescription())               
        self.pipeline_description.Passes.value.append(avango.gua.nodes.SSAAPassDescription())
        self.pipeline_description.EnableABuffer.value = True # enable transparency support



        ## init head node
        self.head_node = avango.gua.nodes.TransformNode(Name = "head_node" + str(self.id))

        #Untracked Version
        self.head_node.Transform.value = avango.gua.make_trans_mat(0.0, 4.0, 10.0)

        #Tracked Version
        #self.head_node.Transform.value = avango.gua.make_trans_mat(0.0, 0.0, 1.0)
        NAVIGATION_NODE.Children.value.append(self.head_node)

        if HEADTRACKING_SENSOR_STATION != "": # headtracking station defined
            self.headtracking_sensor = avango.daemon.nodes.DeviceSensor(DeviceService = avango.daemon.DeviceService())
            self.headtracking_sensor.Station.value = HEADTRACKING_SENSOR_STATION
            self.headtracking_sensor.TransmitterOffset.value = TRACKING_TRANSMITTER_OFFSET
            self.headtracking_sensor.ReceiverOffset.value = avango.gua.make_identity_mat()

            #Tracked Version
            self.head_node.Transform.connect_from(self.headtracking_sensor.Matrix)


        ## init camera node
        self.camera_node = avango.gua.nodes.CameraNode(Name = "camera_node")
        self.camera_node.SceneGraph.value = SCENEGRAPH.Name.value
        self.camera_node.LeftScreenPath.value = SCREEN_NODE.Path.value
        self.camera_node.RightScreenPath.value = SCREEN_NODE.Path.value        
        self.camera_node.NearClip.value = 0.1 # in meter
        self.camera_node.FarClip.value = 100.0 # in meter
        self.camera_node.Resolution.value = WINDOW_RESOLUTION
        self.camera_node.OutputWindowName.value = self.window.Title.value
        self.camera_node.PipelineDescription.value = self.pipeline_description
        self.camera_node.EnableStereo.value = True
        self.camera_node.BlackList.value = ["invisible"]
        self.head_node.Children.value = [self.camera_node]


        ## apply warp-matrices (for projectior registration on DLP wall)
        if WARP_MATRIX_RED_RIGHT != "":
            self.window.WarpMatrixRedRight.value = WARP_MATRIX_RED_RIGHT

        if WARP_MATRIX_GREEN_RIGHT != "":
            self.window.WarpMatrixGreenRight.value = WARP_MATRIX_GREEN_RIGHT

        if WARP_MATRIX_BLUE_RIGHT != "":
            self.window.WarpMatrixBlueRight.value = WARP_MATRIX_BLUE_RIGHT
            
        if WARP_MATRIX_RED_LEFT != "":
            self.window.WarpMatrixRedLeft.value = WARP_MATRIX_RED_LEFT

        if WARP_MATRIX_GREEN_LEFT != "":
            self.window.WarpMatrixGreenLeft.value = WARP_MATRIX_GREEN_LEFT

        if WARP_MATRIX_BLUE_LEFT != "":
            self.window.WarpMatrixBlueLeft.value = WARP_MATRIX_BLUE_LEFT

        #self.set_eye_distance(0.00000)
        self.set_eye_distance(0.064)
        
        #self.enable_videocamera_override(1.0)

    ### functions ###
    def set_eye_distance(self, FLOAT):
        self.camera_node.EyeDistance.value = FLOAT
    """
    def enable_videocamera_override(self, FLAG): # triggerd by Application.py
        if FLAG == True:            
            if self.headtracking_sensor != "": # guard
                #self.tracking_sensor.Station.value = "tracking-dlp-video-camera" # override
                self.headtracking_sensor.Station.value = "tracking-dbl-video-camera" # override                                
        
            for _camera in self.get_camera_list():
                _camera.set_eye_distance(0.0)            

        else:
            if self.headtracking_sensor != "": # guard
                self.headtracking_sensor.Station.value = self.headtracking_sensor
                
            for _camera in self.get_camera_list():
                _camera.set_eye_distance(self.eye_distance)
 
        print(FLAG, "done", self.headtracking_sensor.Station.value, self.headtracking_sensor)
    """


class MultiUserViewingSetup:

    ### constructor
    def __init__(self,
        SCENEGRAPH = None,
        WINDOW_RESOLUTION = avango.gua.Vec2ui(1920, 1200), # default resolution in pixel
        SCREEN_DIMENSIONS = avango.gua.Vec2(4.2, 2.61), # default screen size in meter
        SCREEN_MATRIX = avango.gua.make_identity_mat(),
        TRACKING_TRANSMITTER_OFFSET = avango.gua.make_identity_mat(),
        LEFT_POSITION = avango.gua.Vec2ui(0, 0),
        LEFT_RESOLUTION = avango.gua.Vec2ui(1920, 1200),
        RIGHT_POSITION = avango.gua.Vec2ui(1920, 0),
        RIGHT_RESOLUTION = avango.gua.Vec2ui(1920, 1200),
        DISPLAY_STRING_LIST = [":0.0"],
        WARP_MATRIX_RED_RIGHT = "",
        WARP_MATRIX_GREEN_RIGHT = "",
        WARP_MATRIX_BLUE_RIGHT = "",
        WARP_MATRIX_RED_LEFT = "",
        WARP_MATRIX_GREEN_LEFT = "",
        WARP_MATRIX_BLUE_LEFT = "",
        ):


        ## parameter quards
        if SCENEGRAPH is None:
            print("ERROR: scengraph instance missing")            
            quit()


        ### external references ###
        self.SCENEGRAPH = SCENEGRAPH

        ### parameters ###
        self.window_resolution = WINDOW_RESOLUTION
        self.screen_dimensions = SCREEN_DIMENSIONS
        self.screen_mat = SCREEN_MATRIX
        self.left_resolution = LEFT_RESOLUTION
        self.right_resolution = RIGHT_RESOLUTION        
        self.left_position = LEFT_POSITION
        self.right_position = RIGHT_POSITION

        self.tracking_transmitter_offset = TRACKING_TRANSMITTER_OFFSET

        self.display_string_list = DISPLAY_STRING_LIST

        self.warp_matrix_red_right = WARP_MATRIX_RED_RIGHT
        self.warp_matrix_green_right = WARP_MATRIX_GREEN_RIGHT
        self.warp_matrix_blue_right = WARP_MATRIX_BLUE_RIGHT
        self.warp_matrix_red_left = WARP_MATRIX_RED_LEFT
        self.warp_matrix_green_left = WARP_MATRIX_GREEN_LEFT
        self.warp_matrix_blue_left = WARP_MATRIX_BLUE_LEFT


 
        ### variables ###
        self.user_list = []


        ### resources ###
        
        self.shell = GuaVE()


        ## init viewer
        self.viewer = avango.gua.nodes.Viewer()
        self.viewer.SceneGraphs.value = [self.SCENEGRAPH]
        #self.viewer.Windows.value = [self.window]
        self.viewer.DesiredFPS.value = 200.0 # in Hz
        

        ## init navigation node
        self.navigation_node = avango.gua.nodes.TransformNode(Name = "navigation_node")
        self.SCENEGRAPH.Root.value.Children.value.append(self.navigation_node)
        


        ## init screen node
        self.screen_node = avango.gua.nodes.ScreenNode(Name = "screen_node")
        self.screen_node.Width.value = self.screen_dimensions.x
        self.screen_node.Height.value = self.screen_dimensions.y
        self.screen_node.Transform.value = self.screen_mat
        self.navigation_node.Children.value.append(self.screen_node)



    def init_user(self,
        HEADTRACKING_SENSOR_STATION = "",
        ):
        

        _display_string = self.display_string_list[len(self.user_list)]

        _user = User(
            SCENEGRAPH = self.SCENEGRAPH,
            NAVIGATION_NODE = self.navigation_node,
            SCREEN_NODE = self.screen_node,
            DISPLAY_STRING = _display_string,
            WINDOW_RESOLUTION = self.window_resolution,
            SCREEN_DIMENSIONS = self.screen_dimensions,
            SCREEN_MATRIX = self.screen_mat,
            HEADTRACKING_SENSOR_STATION = HEADTRACKING_SENSOR_STATION,
            TRACKING_TRANSMITTER_OFFSET = self.tracking_transmitter_offset,
            LEFT_POSITION = self.left_position,
            LEFT_RESOLUTION = self.left_resolution,
            RIGHT_POSITION = self.right_position,
            RIGHT_RESOLUTION = self.right_resolution,
            WARP_MATRIX_RED_RIGHT = self.warp_matrix_red_right,
            WARP_MATRIX_GREEN_RIGHT = self.warp_matrix_green_right,
            WARP_MATRIX_BLUE_RIGHT = self.warp_matrix_blue_right,
            WARP_MATRIX_RED_LEFT = self.warp_matrix_red_left,
            WARP_MATRIX_GREEN_LEFT = self.warp_matrix_green_left,
            WARP_MATRIX_BLUE_LEFT = self.warp_matrix_blue_left,
            )
        
        self.user_list.append(_user)

        self.viewer.Windows.value.append(_user.window)


    def run(self, LOCALS, GLOBALS):
        self.shell.start(LOCALS, GLOBALS)
        self.viewer.run()


    def list_variabels(self):
        self.shell.list_variables()



