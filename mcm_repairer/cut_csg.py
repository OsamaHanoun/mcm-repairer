from mcm_repairer.file_io import load_stl, export_mesh_list, export_to_stl
from mcm_repairer.utility import add_prefix_if_exists
from mcm_repairer.geometry_generator import (
    create_solid_from_polygons,
    convert_shape_to_mesh,
    extract_vertices_and_faces_from_mesh,
    create_compound,
)

import numpy as np
from trimesh import Trimesh, primitives, constants, points


empty_mesh = Trimesh(vertices=[], faces=[])


def find_fully_contained_meshes(target_mesh, mesh_list):
    fully_contained_list = []
    remaining_meshes = []

    for mesh in mesh_list:
        if all(target_mesh.contains(mesh.vertices)):
            fully_contained_list.append(mesh)
        else:
            remaining_meshes.append(mesh)

    return fully_contained_list, remaining_meshes


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


def find_intersecting_meshes(target_mesh, mesh_list):
    intersecting_list = []
    remaining_meshes = []

    for mesh in mesh_list:
        if not target_mesh.intersection(mesh).is_empty:
            intersecting_list.append(mesh)
        else:
            remaining_meshes.append(mesh)

    return intersecting_list, remaining_meshes


def merge_close_vertices(vertices):
    cloud = points.PointCloud(vertices)
    cloud.merge_vertices()
    return cloud


def repair_mesh(mesh, merge_tol):
    if mesh.is_empty:
        return mesh

    stored_tol = constants.tol.merge
    constants.tol.merge = merge_tol
    cloud = merge_close_vertices(mesh.vertices)
    constants.tol.merge = stored_tol

    return cloud.convex_hull if len(cloud.vertices) >= 4 else empty_mesh.copy()


def create_container(size, y_position):
    container = primitives.Box(extents=[size, size, size])
    translation_vector = [0, y_position, 0]
    container.apply_translation(translation_vector)
    return container


def trim_csg(sample_file_path, container_size, cover, min_volume, merge_tol):
    mesh_list = load_stl(sample_file_path)
    container = create_container(container_size, container_size / 2)

    smaller_container_size = container_size - cover * 2
    smaller_container = create_container(
        smaller_container_size, smaller_container_size / 2 + cover
    )

    result_mesh_list = []

    for mesh in mesh_list:
        mesh = mesh.intersection(smaller_container)
        mesh = repair_mesh(mesh, merge_tol)

        if not mesh.is_empty and (mesh.volume > min_volume):
            result_mesh_list.append(mesh)

    export_mesh_list(
        [container] + result_mesh_list,
        sample_file_path,
        "trim_csg_",
    )
