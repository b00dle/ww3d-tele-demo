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