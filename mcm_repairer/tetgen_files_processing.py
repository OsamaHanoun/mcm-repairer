import trimesh
import numpy as np
from os.path import split, splitext, join
from mcm_repairer.file_io import load_stl, export_mesh_list


def parse_skipped_faces(faces_file_path):
    skipped_face_dict = {}
    with open(faces_file_path, "r") as faces_file:
        next(faces_file)  # Skip header
        for line in faces_file:
            parts = line.strip().split()
            if len(parts) == 5:
                face_id = int(parts[0])
                node_id_list = list(map(int, parts[1:-1]))
                for node_id in node_id_list:
                    if node_id not in skipped_face_dict:
                        skipped_face_dict[node_id] = []
                    skipped_face_dict[node_id].append(face_id)
    return skipped_face_dict


def parse_nodes(nodes_file_path, skipped_face_dict):
    node_dict = {}
    with open(nodes_file_path, "r") as nodes_file:
        next(nodes_file)  # Skip header
        for line in nodes_file:
            parts = line.strip().split()
            if len(parts) == 4:
                node_id = int(parts[0])
                if node_id in skipped_face_dict:
                    coordinates = list(map(float, parts[1:]))
                    node_dict[node_id] = coordinates
    return node_dict


def is_within_tolerance(node, target_nodes, tolerance):
    node = np.array(node)
    target_nodes = np.array(target_nodes)
    distances = np.linalg.norm(target_nodes - node, axis=1)
    return np.any(distances <= tolerance)


def filter_meshes_by_nodes(meshes, node_list, tolerance=1e-5):
    result_meshes = []
    node_array = np.array(node_list)

    for mesh in meshes:
        # Use trimesh.proximity.ProximityQuery to find nearest points
        proximity_query = trimesh.proximity.ProximityQuery(mesh)

        # Compute distances from each node to the closest vertex in the mesh
        distances, _ = proximity_query.vertex(node_array)

        # Check if any distance is within the tolerance
        min_distance = distances.min()
        if min_distance <= tolerance:
            result_meshes.append(mesh)

    return result_meshes


def remove_filtered_meshes(original_meshes, filtered_meshes):
    # Use set for faster lookup
    filtered_set = set(filtered_meshes)
    # Create a new list excluding the filtered meshes
    remaining_meshes = [mesh for mesh in original_meshes if mesh not in filtered_set]
    return remaining_meshes


def write_failed_meshes(file_path):
    dir_name, base_name = split(file_path)
    file_name, _ = splitext(base_name)

    skipped_faces_file_path = join(dir_name, file_name + "_skipped.face")
    skipped_face_dict = parse_skipped_faces(skipped_faces_file_path)

    nodes_file_path = join(dir_name, file_name + "_skipped.node")
    node_dict = parse_nodes(nodes_file_path, skipped_face_dict)
    node_list = list(node_dict.values())

    mesh_list = load_stl(file_path)

    # filtered_meshes = filter_meshes_by_nodes(mesh_list, node_list)
    filtered_meshes = filter_meshes_by_nodes(mesh_list, node_list)
    remaining_meshes = remove_filtered_meshes(mesh_list, filtered_meshes)

    print(f"found {len(filtered_meshes)} meshes ")

    if len(filtered_meshes) > 0:
        export_mesh_list(filtered_meshes, file_path, "tetgen_invalid_meshes_")
        export_mesh_list(remaining_meshes, file_path, "tetgen_valid_meshes_")
