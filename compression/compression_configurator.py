import avango
import avango.script
import copy

from avango.script import field_has_changed

from input.device import KeyboardDevice
from compression import compression_globals as cg

class CompressionConfigurator(avango.script.Script):
    ''' 
    class used to configure a SPoints node based on key input. 
        Can modify:
            - grid dimensions
            - point precision 
    See get_usage_hint for more info.
    '''
    Keyboard = KeyboardDevice()
    Updated = avango.SFBool()
    
    def __init__(self):
        self.super(CompressionConfigurator).__init__()
        
        # stores the SPointsNode to perform updates on 
        self.spoints_geode = None
        
        # states whether or not output is automatically printed by instance
        self.verbose = True
        
        # stores current settings applied to node
        self._settings = {
            "point_precision" : [4,4,4],
            "color_precision" : [4,4,4],
            "grid_dimension" : [2,2,2],
            "point_size" : 1
        }

        # flipped to true whenever the spoints nodes
        # configurations is changes
        self.Updated.value = False

        # flags for reacting to key press
        # only key down should trigger updates
        self._have_reduced_grid = False
        self._have_increased_grid = False
        self._have_reduced_points = False
        self._have_increased_points = False
        self._have_reduced_color = False
        self._have_increased_color = False
        self._have_reduced_point_size = False
        self._have_increased_point_size = False
        
        self.always_evaluate(True)

    def get_usage_hint(self):
        return """
################# CompressionConfigurator usage ##############
- Press A or D 
  - (uniformly) reduce or increase compression point precision
  - [min, max] = [1, 32]
- Press S or W 
  - (uniformly) reduce or increase compression color precision
  - [min, max] = [1, 32]
- Press Left or Right 
  - (uniformly) reduce or increase compression grid dimensions
  - [min, max] = [1, 16]
- Press O or P 
  - reduce or increase screen space point size
  - [min, max] = [1, 10]
##############################################################
        """

    def get_settings(self):
        ''' returns a copy of the current settings applied to node. '''
        return {
            key : copy.deepcopy(value)
            for key, value in self._settings.items()
        }
        
    def set_spoints_geode(self, node):
        ''' Sets the SPointsNode configured by this instance. '''
        self.spoints_geode = node
        if self.spoints_geode is not None:
            self.update_spoints_geode()

    def reduce_point_precision(self):
        if min(self._settings["point_precision"]) > 1:
            self._settings["point_precision"] = [p-1 for p in self._settings["point_precision"]]
            self.update_spoints_geode()

    def increase_point_precision(self):
        if max(self._settings["point_precision"]) < 32:
            self._settings["point_precision"] = [p+1 for p in self._settings["point_precision"]]
            self.update_spoints_geode()

    def reduce_color_precision(self):
        if min(self._settings["color_precision"]) > 1:
            self._settings["color_precision"] = [p-1 for p in self._settings["color_precision"]]
            self.update_spoints_geode()

    def increase_color_precision(self):
        if max(self._settings["color_precision"]) < 32:
            self._settings["color_precision"] = [p+1 for p in self._settings["color_precision"]]
            self.update_spoints_geode()

    def reduce_grid_dimensions(self):
        if min(self._settings["grid_dimension"]) > 1:
            self._settings["grid_dimension"] = [g-1 for g in self._settings["grid_dimension"]]
            self.update_spoints_geode()

    def increase_grid_dimensions(self):
        if max(self._settings["grid_dimension"]) < 16:
            self._settings["grid_dimension"] = [g+1 for g in self._settings["grid_dimension"]]
            self.update_spoints_geode()

    def reduce_point_size(self):
        if self._settings["point_size"] > 1:
            self._settings["point_size"] = self._settings["point_size"] - 1
            self.update_spoints_geode()

    def increase_point_size(self):
        if self._settings["point_size"] < 10:
            self._settings["point_size"] = self._settings["point_size"] + 1
            self.update_spoints_geode()
    
    def update_spoints_geode(self):
        cg.set_grid_dimensions(self.spoints_geode, self._settings["grid_dimension"]) 
        cg.set_point_precision(self.spoints_geode, self._settings["point_precision"])
        cg.set_color_precision(self.spoints_geode, self._settings["color_precision"])
        cg.set_point_size(self.spoints_geode, self._settings["point_size"])
        self.Updated.value = True
        if self.verbose:
            out_str = "\n=====Compression Settings=====\n"
            for key, value in self._settings.items():
                out_str += key + ": " + str(value) + "\n"
            out_str += "=============================="
            print(out_str)

    def evaluate(self):
        ''' Called each frame. '''
        if self.Updated.value:
            self.Updated.value = False
        self._evaluate_point_precision()
        self._evaluate_color_precision()
        self._evaluate_grid_dimensions()
        self._evaluate_point_size()
    
    def _evaluate_point_precision(self):
        ''' process changes in point precision
            and update spoints_geode accordingly. '''
        if self.Keyboard.KeyA.value and not self._have_reduced_points:
            self._have_reduced_points = True
            self.reduce_point_precision()
        elif not self.Keyboard.KeyA.value and self._have_reduced_points:
            self._have_reduced_points = False
        elif self.Keyboard.KeyD.value and not self._have_increased_points:
            self._have_increased_points = True
            self.increase_point_precision()
        elif not self.Keyboard.KeyD.value and self._have_increased_points:
            self._have_increased_points = False

    def _evaluate_color_precision(self):
        ''' process changes in color precision
            and update spoints_geode accordingly. '''
        if self.Keyboard.KeyS.value and not self._have_reduced_color:
            self._have_reduced_color = True
            self.reduce_color_precision()
        elif not self.Keyboard.KeyS.value and self._have_reduced_color:
            self._have_reduced_color = False
        elif self.Keyboard.KeyW.value and not self._have_increased_color:
            self._have_increased_color = True
            self.increase_color_precision()
        elif not self.Keyboard.KeyW.value and self._have_increased_color:
            self._have_increased_color = False

    def _evaluate_grid_dimensions(self):
        ''' process changes in grid dimensions
            and update spoints_geode accordingly. '''
        if self.Keyboard.KeyLeft.value and not self._have_reduced_grid:
            self._have_reduced_grid = True
            self.reduce_grid_dimensions()
        elif not self.Keyboard.KeyLeft.value and self._have_reduced_grid:
            self._have_reduced_grid = False
        elif self.Keyboard.KeyRight.value and not self._have_increased_grid:
            self._have_increased_grid = True
            self.increase_grid_dimensions()
        elif not self.Keyboard.KeyRight.value and self._have_increased_grid:
            self._have_increased_grid = False

    def _evaluate_point_size(self):
        ''' process changes in grid dimensions
            and update spoints_geode accordingly. '''
        if self.Keyboard.KeyO.value and not self._have_reduced_point_size:
            self._have_reduced_point_size = True
            self.reduce_point_size()
        elif not self.Keyboard.KeyO.value and self._have_reduced_point_size:
            self._have_reduced_point_size = False
        elif self.Keyboard.KeyP.value and not self._have_increased_point_size:
            self._have_increased_point_size = True
            self.increase_point_size()
        elif not self.Keyboard.KeyP.value and self._have_increased_point_size:
            self._have_increased_point_size = False