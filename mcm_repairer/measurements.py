from OCC.Core.BRepGProp import brepgprop_VolumeProperties
from OCC.Core.GProp import GProp_GProps
from OCC.Core.TopoDS import TopoDS_Shape
from OCC.Core.TopAbs import TopAbs_SOLID
from OCC.Core.TopExp import TopExp_Explorer


def get_volume(shape: TopoDS_Shape) -> float:
    properties = GProp_GProps()
    brepgprop_VolumeProperties(shape, properties)
    return properties.Mass()


def has_sub_shapes(shape):
    explorer = TopExp_Explorer(shape, TopAbs_SOLID)
    return explorer.More()
