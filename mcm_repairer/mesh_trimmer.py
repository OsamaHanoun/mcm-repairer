from mcm_repairer.file_io import load_stl, export_mesh_list, export_to_stl
from mcm_repairer.utility import add_prefix_if_exists
from mcm_repairer.geometry_generator import (
    create_solid_from_polygons,
    convert_shape_to_mesh,
    extract_vertices_and_faces_from_mesh,
    create_compound,
)

import numpy as np
from trimesh import Trimesh
from OCC.Core.BRepAlgoAPI import (
    BRepAlgoAPI_Fuse,
    BRepAlgoAPI_Common,
)


def create_scaled_mesh_by_shift(mesh, expansion_distance):
    centroid = mesh.centroid
    vertices = mesh.vertices
    directions = vertices - centroid
    norms = np.linalg.norm(directions, axis=1).reshape(-1, 1)

    # Avoid division by zero for vertices exactly at the centroid
    norms[norms == 0] = 1

    directions_normalized = directions / norms
    new_vertices = vertices + directions_normalized * expansion_distance

    # Create a new mesh from the new vertices using the convex hull
    new_mesh = Trimesh(vertices=new_vertices)

    return new_mesh.convex_hull


def find_fully_contained_meshes(target_mesh, mesh_list):
    fully_contained_list = []
    remaining_meshes = []

    for mesh in mesh_list:
        if all(target_mesh.contains(mesh.vertices)):
            fully_contained_list.append(mesh)
        else:
            remaining_meshes.append(mesh)

    return fully_contained_list, remaining_meshes


def find_intersecting_meshes(target_mesh, mesh_list):
    intersecting_list = []
    remaining_meshes = []

    for mesh in mesh_list:
        if not target_mesh.intersection(mesh).is_empty:
            intersecting_list.append(mesh)
        else:
            remaining_meshes.append(mesh)

    return intersecting_list, remaining_meshes


def find_meshes_with_centroid_inside_target_mesh(target_mesh, mesh_list):
    inside_target = []
    remaining_meshes = []

    for mesh in mesh_list:
        if target_mesh.contains([mesh.centroid])[0]:
            inside_target.append(mesh)
        else:
            remaining_meshes.append(mesh)

    return inside_target, remaining_meshes


def convert_solid_to_trimesh(solid):
    convert_shape_to_mesh(solid)
    vertices, faces = extract_vertices_and_faces_from_mesh(solid)
    return Trimesh(vertices=vertices, faces=faces)


def merge_meshes_surfaces_with_target_mesh(
    target_mesh, mesh_list, sample_file_path, container_file_path
):
    target_solid = create_solid_from_polygons(target_mesh.faces, target_mesh.vertices)
    solid_list = [
        create_solid_from_polygons(mesh.faces, mesh.vertices) for mesh in mesh_list
    ]

    result = []

    for solid in solid_list:
        common = BRepAlgoAPI_Common(solid, target_solid).Shape()
        result.append(common)
        target_solid = BRepAlgoAPI_Fuse(target_solid, common).Shape()

    print("Start converting solids to a single mesh")
    result.append(target_solid)
    for shape in result:
        convert_shape_to_mesh(shape)

    shapes_compound = create_compound(result)

    return shapes_compound


def trim(
    sample_file_path,
    container_file_path,
    min_gap,
    # min_volume,
    # min_area,
    # min_aspect_ratio,
):
    # has: meshes, container mesh

    container = load_stl(container_file_path)[0]
    mesh_list = load_stl(sample_file_path)

    # create a scaled down mesh of the container by min gap
    scaled_container = create_scaled_mesh_by_shift(container, -min_gap)

    # create hollow container
    hollow_container = container.difference(scaled_container)  # type: ignore

    # meshes won't need any operations. add them when exporting
    fully_contained_meshes, remaining_meshes = find_fully_contained_meshes(
        scaled_container, mesh_list
    )

    # meshes that intersect with the hollow shape
    intersecting_meshes, _ = find_intersecting_meshes(
        hollow_container, remaining_meshes
    )

    # meshes (inner_surface) that we need to cut or ensure minimum gap
    # meshes (outer_surface_meshes) that need to be shipped to pythonocc
    inner_surface_meshes, outer_surface_meshes = find_fully_contained_meshes(
        container, intersecting_meshes
    )

    # filter out inside_meshes with center on the solid part
    _, inner_surface_meshes = find_meshes_with_centroid_inside_target_mesh(
        hollow_container, inner_surface_meshes
    )

    # Todo: cut inner_surface using hollow shape to ensure gap or you can scale down meshes

    # cut outer surface meshes using the container
    shapes_compound = merge_meshes_surfaces_with_target_mesh(
        container, outer_surface_meshes, sample_file_path, container_file_path
    )  # type: ignore
    f = add_prefix_if_exists(sample_file_path, prefix="trim_1_result_")
    export_to_stl(shapes_compound, f)

    export_mesh_list(
        fully_contained_meshes + inner_surface_meshes,
        sample_file_path,
        "trim_2_result_",
    )

    # ensure:
    # minimum gap between meshes and the container
    # minimum surface area -> undo trim and scale down mesh if it didn't work out
    # minimum aspect ration

    # cut mesh using pythonocc
