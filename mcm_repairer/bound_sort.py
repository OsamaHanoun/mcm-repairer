from OCC.Core.Bnd import Bnd_Box, Bnd_BoundSortBox, Bnd_HArray1OfBox
from OCC.Core.BRepBndLib import brepbndlib_Add
from OCC.Core.TColStd import TColStd_ListOfInteger, TColStd_ListIteratorOfListOfInteger  # type: ignore
from OCC.Core.TopoDS import TopoDS_Shape

from typing import Dict, List, Tuple, Any

TBndDict = Dict[int, Tuple[Bnd_Box, TopoDS_Shape]]


def convert_occ_list_to_py_list(occ_list: TColStd_ListOfInteger) -> List[int]:
    list: List[int] = []
    iterator: Any = TColStd_ListIteratorOfListOfInteger(occ_list)
    while iterator.More():
        list.append(iterator.Value())
        iterator.Next()
    return list


def create_bound_sort_box(
    solid_list: list[TopoDS_Shape],
) -> Tuple[Bnd_BoundSortBox, TBndDict]:
    bnd_dict: TBndDict = dict()
    bnd_box_array = Bnd_HArray1OfBox(0, len(solid_list))

    for i, solid in enumerate(solid_list):
        bnd_box = Bnd_Box()
        brepbndlib_Add(solid, bnd_box)
        bnd_dict[i] = (bnd_box, solid)
        bnd_box_array.SetValue(i, bnd_box)

    bnd_sort_box = Bnd_BoundSortBox()
    bnd_sort_box.Initialize(bnd_box_array)

    return (bnd_sort_box, bnd_dict)
