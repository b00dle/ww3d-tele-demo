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

def set_color_precision(spoints_geode, prec):
    if len(prec) == 3:
        spoints_geode.GlobalColorPrecisionX.value = prec[0]
        spoints_geode.GlobalColorPrecisionY.value = prec[1]
        spoints_geode.GlobalColorPrecisionZ.value = prec[2]

def set_point_size(spoints_geode, size):
    spoints_geode.ScreenSpacePointSize.value = size

def set_global_comp_lvl(video3d_geode, val):
    video3d_geode.GlobalCompressionLevel.value = val

def set_depth_comp_lvl(video3d_geode, val):
    video3d_geode.DepthCompressionLevel.value = val

def set_color_comp_lvl(video3d_geode, val):
    video3d_geode.ColorCompressionLevel.value = val