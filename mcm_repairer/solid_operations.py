from mcm_repairer.bound_sort import create_bound_sort_box, convert_occ_list_to_py_list
from mcm_repairer.utility import safe_access, safe_dict_setter
from mcm_repairer.measurements import has_sub_shapes

from OCC.Core.TopoDS import TopoDS_Shape
from OCC.Core.TColStd import TColStd_ListOfInteger
from OCC.Core.BRepAlgoAPI import (
    BRepAlgoAPI_Fuse,
    BRepAlgoAPI_Common,
    BRepAlgoAPI_Cut,
)


def remove_overlaps_from_solids(
    shape_list: list[TopoDS_Shape], cover_thickness: float
) -> list[TopoDS_Shape]:
    bnd_sort_box, bnd_map = create_bound_sort_box(shape_list, cover_thickness)
    checked_shape_dict: dict[int, dict[int, int]] = dict()
    empty_shape = TopoDS_Shape()
    has_cover = cover_thickness > 0

    for i, shape in enumerate(shape_list):
        bnd_box = bnd_map[i][0]
        bnd_index_occ_list: TColStd_ListOfInteger = bnd_sort_box.Compare(bnd_box)
        bnd_index_list = convert_occ_list_to_py_list(bnd_index_occ_list)

        for touched_bnd_index in bnd_index_list:
            if touched_bnd_index == i or safe_access(
                checked_shape_dict, touched_bnd_index, i
            ):
                continue

            safe_dict_setter(checked_shape_dict, i, touched_bnd_index, True)
            touched_shape = bnd_map[touched_bnd_index][1]
            touched_bnd = bnd_map[touched_bnd_index][0]
            common = BRepAlgoAPI_Common(shape, touched_shape).Shape()

            if not has_sub_shapes(common) and not has_cover:
                continue

            scaled_shape = bnd_map[i][2]
            scaled_touched_shape = bnd_map[touched_bnd_index][2]

            if has_sub_shapes(common):
                bnd_map[i] = (
                    bnd_box,
                    BRepAlgoAPI_Cut(shape, common).Shape(),
                    scaled_shape if has_cover else empty_shape,
                )
                bnd_map[touched_bnd_index] = (
                    touched_bnd,
                    BRepAlgoAPI_Fuse(touched_shape, common).Shape(),
                    scaled_touched_shape if has_cover else empty_shape,
                )
            else:
                bnd_map[touched_bnd_index] = (
                    touched_bnd,
                    BRepAlgoAPI_Cut(touched_shape, scaled_shape).Shape(),
                    scaled_touched_shape,
                )

    modified_solid_list: list[TopoDS_Shape] = []
    for value in bnd_map.values():
        modified_solid_list.append(value[1])

    return modified_solid_list
