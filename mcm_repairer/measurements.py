from OCC.Core.BRepGProp import brepgprop_VolumeProperties
from OCC.Core.GProp import GProp_GProps
from OCC.Core.TopoDS import TopoDS_Shape


def get_volume(shape: TopoDS_Shape) -> float:
    properties = GProp_GProps()
    brepgprop_VolumeProperties(shape, properties)
    return properties.Mass()
