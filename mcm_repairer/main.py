from time import time

from mcm_repairer.file_io import load_stl, export_to_stl
from mcm_repairer.utility import add_prefix_if_exists
from mcm_repairer.geometry_generator import (
    create_solid_from_polygons,
    create_compound,
    convert_shape_to_mesh,
)
from mcm_repairer.solid_operations import remove_overlaps_from_solids
from mcm_repairer.tetgen_files_processing import write_failed_meshes


def repair_model(file_path, cover_thickness: float):
    start_time = time()
    print("Start loading STL file ")
    meshes = load_stl(file_path)
    solid_list = []
    print(f"STL file has {len(meshes)} meshes")

    print("Start creating brep solids from meshes")
    for mesh in meshes:
        solid = create_solid_from_polygons(mesh.faces, mesh.vertices)  # type: ignore
        solid_list.append(solid)
    print(f"{len(solid_list)} solids were created")

    print("Start repairing solids")
    unoverlapped_shape_list = remove_overlaps_from_solids(solid_list, cover_thickness)
    print(f"{len(unoverlapped_shape_list)} solids after were repairment")

    print("Start converting solids to a single mesh")
    for shape in unoverlapped_shape_list:
        convert_shape_to_mesh(shape)
    shapes_compound = create_compound(unoverlapped_shape_list)

    print("Start exporting meshes to STL")
    result_file_path = add_prefix_if_exists(file_path)
    export_to_stl(shapes_compound, result_file_path)

    print("--- %s seconds ---" % (round(time() - start_time)))
