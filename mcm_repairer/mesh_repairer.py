from mcm_repairer.file_io import load_stl, export_mesh_list

from decimal import Decimal
from time import time
import numpy as np

from trimesh.points import PointCloud
from trimesh import constants, Trimesh
from trimesh.collision import CollisionManager
from trimesh.proximity import ProximityQuery


def calculate_total_volume(mesh_list):
    return sum(mesh.volume for mesh in mesh_list)


def create_scaled_mesh_to_shift(mesh, size_shift):
    scale_factor = 1 + (size_shift / mesh.extents.max())
    scaled_mesh = mesh.copy()
    scaled_mesh.apply_scale(scale_factor)
    translation_vector = mesh.centroid - scaled_mesh.centroid
    scaled_mesh.apply_translation(translation_vector)

    return scaled_mesh


def create_scaled_mesh_to_volume(mesh, target_volume):
    current_volume = mesh.volume
    scale_factor = (target_volume / current_volume) ** (1 / 3)
    scaled_mesh = mesh.copy()
    scaled_mesh.apply_scale(scale_factor)
    translation_vector = mesh.centroid - scaled_mesh.centroid
    scaled_mesh.apply_translation(translation_vector)
    return scaled_mesh


def max_negative_value(a, b):
    if a < 0 and b < 0:
        return max(a, b)
    elif a < 0:
        return a
    elif b < 0:
        return b
    else:
        return None


def create_scaled_mesh_list(mesh_list, size_shift):
    scaled_mesh_list = []

    if size_shift <= 0:
        return mesh_list.copy()

    for mesh in mesh_list:
        scaled_mesh = create_scaled_mesh_to_shift(mesh, size_shift)
        scaled_mesh_list.append(scaled_mesh)

    return scaled_mesh_list


def merge_close_vertices(vertices):
    cloud = PointCloud(vertices)
    cloud.merge_vertices()
    return cloud


def repair_scaled_meshes(mesh_dict, scaled_mesh_key_list, merge_tol):
    stored_tol = constants.tol.merge

    for key in scaled_mesh_key_list:
        mesh = mesh_dict[key]
        if mesh.is_empty:
            continue
        constants.tol.merge = merge_tol
        cloud = merge_close_vertices(mesh.vertices)
        constants.tol.merge = stored_tol
        mesh_dict[key] = cloud.convex_hull


def ensure_min_gap(
    intersected_pairs_list, mesh_dict, scaled_mesh_list, min_gap, min_volume
):
    scaled_mesh_key_set = set()
    for i, j in intersected_pairs_list:
        mesh_i = mesh_dict[i]
        mesh_j = mesh_dict[j]

        if mesh_i.is_empty or mesh_j.is_empty:
            continue

        larger_mesh_key = i if is_mesh_larger(mesh_i, mesh_j) else j
        larger_mesh = mesh_dict[larger_mesh_key]
        larger_scaled_mesh = scaled_mesh_list[larger_mesh_key]

        smaller_mesh_key = j if i == larger_mesh_key else i
        smaller_mesh = mesh_dict[smaller_mesh_key]

        common_scaled_mesh = larger_scaled_mesh.intersection(smaller_mesh)

        # case 1 : has no intersection using original mesh nor using scaled mesh  ->  no gap check needed
        if common_scaled_mesh.is_empty:
            continue

        # case 2 : has intersection using original mesh -> remove overlap and ensure minimum gap
        # case 2.a : the centroid of the smaller mesh is inside the larger mesh -> no scaling could ensure the minimum gap -> sol.1-Todo : scale the larger mesh (can lead to lower volume fraction ) or  sol.2: just remove the smaller mesh (Todo: ensure not both of the meshes will be deleted later on).
        # case 2.b : the centroid of the smaller mesh is outside the larger mesh -> scale the smaller mesh by finding the distance between its centroid and the common mesh.
        # case 2.c : the centroid of the larger mesh is inside the smaller mesh -> just remove the smaller mesh (Todo: ensure not both of the meshes will be deleted later on).
        # case 3 :has intersection using scaled mesh only  ->  ensure minimum gap

        common_original_mesh = larger_mesh.intersection(smaller_mesh)

        if common_original_mesh.is_empty:
            pq_larger_mesh = ProximityQuery(larger_mesh)
            vertices = common_scaled_mesh.vertices
            min_distance = pq_larger_mesh.signed_distance(vertices).min()
            shrinkage_size_shift = min_distance - min_gap
            scaled_mesh = create_scaled_mesh_to_shift(
                smaller_mesh, shrinkage_size_shift
            )
        else:
            scaled_mesh = create_scaled_mesh_to_volume(smaller_mesh, min_volume)

            if larger_scaled_mesh.intersection(smaller_mesh).is_empty:
                pq_scaled_mesh = ProximityQuery(scaled_mesh)
                vertices = larger_scaled_mesh.vertices
                distances = pq_scaled_mesh.signed_distance(vertices)
                min_distance = max_negative_value(distances.min(), distances.max())

                if min_distance is not None:
                    expansion_size_shift = -min_distance
                    scaled_mesh = create_scaled_mesh_to_shift(
                        scaled_mesh, expansion_size_shift
                    )
                    scaled_mesh = create_scaled_mesh_to_volume(
                        smaller_mesh, scaled_mesh.volume
                    )
                else:
                    scaled_mesh = Trimesh(vertices=[], faces=[])
            else:
                scaled_mesh = Trimesh(vertices=[], faces=[])

        # if not scaled_mesh.is_empty:
        #     continue
        # stored_tol = constants.tol.merge
        # constants.tol.merge = 0.3
        # cloud = merge_close_vertices(scaled_mesh.vertices)
        # constants.tol.merge = stored_tol
        # scaled_mesh = cloud.convex_hull
        mesh_dict[smaller_mesh_key] = scaled_mesh
        scaled_mesh_key_set.add(smaller_mesh_key)
    return list(scaled_mesh_key_set)


def find_intersected_meshes(mesh_list, scaled_mesh_list):
    mesh_dict = {}
    manager = CollisionManager()

    for i in range(len(mesh_list)):
        mesh_dict[i] = mesh_list[i]
        manager.add_object(i, scaled_mesh_list[i].bounding_box)

    intersected_pairs_set = set()
    for i in range(len(scaled_mesh_list)):
        collision_key_list = manager.in_collision_single(
            scaled_mesh_list[i].bounding_box, None, True
        )[1]  # type: ignore

        for other_bounding_box_id in collision_key_list:
            if not i == other_bounding_box_id:
                pair = tuple(sorted((i, other_bounding_box_id)))
                intersected_pairs_set.add(pair)

        manager.remove_object(i)

    return intersected_pairs_set, mesh_dict


def is_mesh_larger(mesh_1, mesh_2):
    if mesh_1.volume > mesh_2.volume:
        return True
    else:
        return False


def sort_meshes_by_volume(mesh_1, mesh_2):
    if mesh_1.volume < mesh_2.volume:
        smaller_mesh = mesh_1
        larger_mesh = mesh_2
    else:
        smaller_mesh = mesh_2
        larger_mesh = mesh_1

    return smaller_mesh, larger_mesh


def is_smaller_mesh_fully_contained(mesh_1, mesh_2):
    smaller_mesh, larger_mesh = sort_meshes_by_volume(mesh_1, mesh_2)
    is_contained_list = larger_mesh.contains(smaller_mesh.vertices)
    # Check if every vertex of the smaller mesh is inside the larger mesh
    for is_contained in is_contained_list:
        if not is_contained:
            return False
    return True


def is_smaller_mesh_centroid_inside_larger_mesh(mesh_1, mesh_2):
    smaller_mesh, larger_mesh = sort_meshes_by_volume(mesh_1, mesh_2)
    return larger_mesh.contains([smaller_mesh.centroid])


def filter_out_fully_overlapped_meshes(pairs_set, mesh_dict):
    unwanted_value_list = []
    for pair in pairs_set:
        i, j = pair
        if is_smaller_mesh_fully_contained(mesh_dict[i], mesh_dict[j]):
            unwanted_value_list.append(pair)

    for pair in unwanted_value_list:
        i, j = pair
        smaller_mesh_key = i if is_mesh_larger(mesh_dict[i], mesh_dict[j]) else j
        del mesh_dict[smaller_mesh_key]
        pairs_set.remove(pair)

    return pairs_set, mesh_dict


def filter_out_smaller_meshes_with_centroid_inside_larger_meshes(pairs_set, mesh_dict):
    unwanted_value_list = []
    for pair in pairs_set:
        i, j = pair
        if is_smaller_mesh_centroid_inside_larger_mesh(mesh_dict[i], mesh_dict[j]):
            unwanted_value_list.append(pair)

    for pair in unwanted_value_list:
        i, j = pair
        smaller_mesh_key = i if is_mesh_larger(mesh_dict[i], mesh_dict[j]) else j
        del mesh_dict[smaller_mesh_key]
        pairs_set.remove(pair)

    return pairs_set, mesh_dict


def filter_out_meshes_by_volume(mesh_dict, scaled_mesh_key_list, min_mesh_volume):
    unwanted_mesh_key_list = [
        key
        for key in scaled_mesh_key_list
        if mesh_dict[key].is_empty or mesh_dict[key].volume <= min_mesh_volume
    ]

    for key in unwanted_mesh_key_list:
        del mesh_dict[key]


def repair(file_path, min_gap, merge_tol, min_mesh_volume):
    start_time = time()

    print("Load STL file ")
    mesh_list = load_stl(file_path)
    imported_mesh_count = len(mesh_list)
    imported_mesh_volume = calculate_total_volume(mesh_list)
    print(
        f"Loaded {imported_mesh_count} watertight meshes with a total volume of {Decimal(imported_mesh_volume):.2E}\n"
    )

    print("Create scaled meshes using the specified minimum gap \n")
    scaled_mesh_list = create_scaled_mesh_list(mesh_list, min_gap)

    print("Find intersected meshes using the scaled meshes")
    intersected_pairs_set, mesh_dict = find_intersected_meshes(
        mesh_list, scaled_mesh_list
    )
    print(
        f"\t> Found {len(intersected_pairs_set)} pairs scaled meshes with possible intersections or close to each other \n"
    )

    print("Filter out fully contained mesh by another larger mesh")
    mesh_dict_count = len(mesh_dict)
    filter_out_fully_overlapped_meshes(intersected_pairs_set, mesh_dict)
    print(f"\t> Removed {len(mesh_dict) - mesh_dict_count} meshes\n")

    print("Filter out mesh with a centroid inside another larger mesh")
    mesh_dict_count = len(mesh_dict)
    filter_out_smaller_meshes_with_centroid_inside_larger_meshes(
        intersected_pairs_set, mesh_dict
    )
    print(f"\t> Removed {len(mesh_dict) - mesh_dict_count} meshes\n")

    print(f"Ensure a minimum gap of {min_gap} between meshes")
    scaled_mesh_key_list = ensure_min_gap(
        intersected_pairs_set, mesh_dict, scaled_mesh_list, min_gap, min_mesh_volume
    )
    print(f"\t> Scaled {len(scaled_mesh_key_list)} meshes due to overlap or low gap \n")

    print(
        "Repair scaled meshes by merging close vertices and then applying convex hull"
    )
    repair_scaled_meshes(mesh_dict, scaled_mesh_key_list, merge_tol)
    print(f"\t> Finished repairing {len(scaled_mesh_key_list)} scaled meshes \n")

    print(f"Filter out meshes with a volume less or equal to {min_mesh_volume}")
    mesh_dict_count = len(mesh_dict)
    filter_out_meshes_by_volume(mesh_dict, scaled_mesh_key_list, min_mesh_volume)
    print(
        f"\t> removed {mesh_dict_count - len(mesh_dict)} meshes due to small volume \n"
    )

    print("Export repaired meshes")
    export_mesh_list(mesh_dict.values(), file_path, "repair_result_")
    exported_mesh_volume = calculate_total_volume(mesh_dict.values())
    volume_reduction_percentage = (
        (imported_mesh_volume - exported_mesh_volume) / imported_mesh_volume * 100
    )
    print(
        f"\t> Exported {len(mesh_dict.values())} meshes out of {imported_mesh_count} imported meshes into a single file"
    )
    print(f"\t> Exported meshes volume is {Decimal(exported_mesh_volume):.2E}")
    print(f"\t> Volume reduction is {Decimal(volume_reduction_percentage):.2E}% /n")

    print("--- %s seconds ---" % (round(time() - start_time)))
