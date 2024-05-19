from mcm_repairer.bound_sort import create_bound_sort_box, convert_occ_list_to_py_list
from mcm_repairer.utility import safe_access, safe_dict_setter

from OCC.Core.TopoDS import TopoDS_Shape
from OCC.Core.TColStd import TColStd_ListOfInteger
from OCC.Core.BRepAlgoAPI import (
    BRepAlgoAPI_Fuse,
    BRepAlgoAPI_Common,
    BRepAlgoAPI_Cut,
)


def remove_overlaps_from_solids(solids: list[TopoDS_Shape]) -> list[TopoDS_Shape]:
    [bnd_sort_box, bnd_map] = create_bound_sort_box(solids)
    checked_shape_dict: dict[int, dict[int, int]] = dict()

    for i, solid in enumerate(solids):
        bnd_box = bnd_map[i][0]
        bnd_index_occ_list: TColStd_ListOfInteger = bnd_sort_box.Compare(bnd_box)
        bnd_index_list = convert_occ_list_to_py_list(bnd_index_occ_list)

        for touched_bnd_index in bnd_index_list:
            if touched_bnd_index == i or safe_access(
                checked_shape_dict, touched_bnd_index, i
            ):
                continue

            safe_dict_setter(checked_shape_dict, i, touched_bnd_index, True)
            touched_solid = bnd_map[touched_bnd_index][1]
            common = BRepAlgoAPI_Common(solid, touched_solid).Shape()

            if common.IsNull():
                continue

            touched_bnd = bnd_map[touched_bnd_index][0]
            bnd_map[i] = (bnd_box, BRepAlgoAPI_Cut(solid, common).Shape())
            bnd_map[touched_bnd_index] = (
                touched_bnd,
                BRepAlgoAPI_Fuse(touched_solid, common).Shape(),
            )

    modified_solid_list: list[TopoDS_Shape] = []
    for value in bnd_map.values():
        modified_solid_list.append(value[1])

    return modified_solid_list
