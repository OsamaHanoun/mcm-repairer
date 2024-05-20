from OCC.Core.Bnd import Bnd_Box, Bnd_BoundSortBox, Bnd_HArray1OfBox
from OCC.Core.BRepBndLib import brepbndlib_Add
from OCC.Core.TColStd import TColStd_ListOfInteger, TColStd_ListIteratorOfListOfInteger  # type: ignore
from OCC.Core.TopoDS import TopoDS_Shape
from OCC.Core.gp import gp_Trsf, gp_Pnt
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform

from typing import Dict, List, Tuple, Any

TBndDict = Dict[int, Tuple[Bnd_Box, TopoDS_Shape, TopoDS_Shape]]


def convert_occ_list_to_py_list(occ_list: TColStd_ListOfInteger) -> List[int]:
    list: List[int] = []
    iterator: Any = TColStd_ListIteratorOfListOfInteger(occ_list)
    while iterator.More():
        list.append(iterator.Value())
        iterator.Next()
    return list


def get_bounding_box_center_and_dimensions(solid):
    bnd_box = Bnd_Box()
    brepbndlib_Add(solid, bnd_box)
    x_min, y_min, z_min, x_max, y_max, z_max = bnd_box.Get()
    center_x = (x_min + x_max) / 2.0
    center_y = (y_min + y_max) / 2.0
    center_z = (z_min + z_max) / 2.0
    dimensions = (x_max - x_min, y_max - y_min, z_max - z_min)
    return gp_Pnt(center_x, center_y, center_z), dimensions


def scale_shape(shape, cover_thickness):
    center, original_dimensions = get_bounding_box_center_and_dimensions(shape)
    new_dimensions = [dim + 2 * cover_thickness for dim in original_dimensions]
    scale_factors = [
        new / original for new, original in zip(new_dimensions, original_dimensions)
    ]
    trsf = gp_Trsf()
    trsf.SetScale(center, max(scale_factors))
    brep_trsf = BRepBuilderAPI_Transform(shape, trsf, True, True)
    scaled_solid = brep_trsf.Shape()

    return scaled_solid


def create_bound_sort_box(
    shape_list: list[TopoDS_Shape], cover_thickness: float
) -> Tuple[Bnd_BoundSortBox, TBndDict]:
    if cover_thickness > 0:
        scaled_shape_list = [
            scale_shape(shape, cover_thickness) for shape in shape_list
        ]
    else:
        scaled_shape_list = shape_list

    bnd_dict: TBndDict = dict()
    bnd_box_array = Bnd_HArray1OfBox(0, len(shape_list))

    for i, scaled_shape in enumerate(scaled_shape_list):
        shape = shape_list[i]
        bnd_box = Bnd_Box()
        brepbndlib_Add(scaled_shape, bnd_box)
        bnd_dict[i] = (bnd_box, shape, scaled_shape)
        bnd_box_array.SetValue(i, bnd_box)
    bnd_sort_box = Bnd_BoundSortBox()
    bnd_sort_box.Initialize(bnd_box_array)

    return bnd_sort_box, bnd_dict
