# type: ignore
from mcm_repairer.file_io import load_stl, export_mesh_list

import trimesh
import numpy as np


def reduce(file_path, vf_target):
    # Load the mesh list
    mesh_list = load_stl(file_path)

    # Calculate the total volume of the current meshes
    volume_total_current = sum(mesh.volume for mesh in mesh_list)
    concat_mesh = trimesh.util.concatenate(mesh_list)
    bnd_box = concat_mesh.bounding_box

    # Calculate current volume fraction based on bounding box volume
    current_vf = volume_total_current / bnd_box.volume
    print("Current volume fraction = ", current_vf)

    # Calculate the target volume fraction with respect to the bounding box volume
    target_volume = bnd_box.volume * (current_vf - vf_target)
    # Calculate the total translation needed
    translate_factor = target_volume / bnd_box.volume

    for mesh in mesh_list:
        direction_vector = mesh.bounding_box.centroid - bnd_box.centroid
        distance_from_center = np.linalg.norm(direction_vector)

        if distance_from_center > 0:
            normalized_direction = direction_vector / distance_from_center
        else:
            normalized_direction = np.zeros_like(direction_vector)

        # Scale translation distance based on the relative distance from the center
        scaled_translate_distance = distance_from_center * translate_factor
        translation_vector = normalized_direction * scaled_translate_distance
        mesh.apply_translation(translation_vector)

    # Recalculate the total volume and volume fraction after translation
    volume_total_current = sum(mesh.volume for mesh in mesh_list)
    concat_mesh = trimesh.util.concatenate(mesh_list)
    bnd_box = concat_mesh.bounding_box
    new_vf = volume_total_current / bnd_box.volume
    print("Volume fraction after reduction = ", new_vf)

    # Export the reduced mesh list
    export_mesh_list(mesh_list, file_path, "reduced_vf_")


def reduce_iteratively(file_path, vf_target, tolerance=0.001, max_iterations=10):
    # Load the mesh list
    mesh_list = load_stl(file_path)

    for iteration in range(max_iterations):
        # Calculate the total volume of the current meshes
        volume_total_current = sum(mesh.volume for mesh in mesh_list)
        concat_mesh = trimesh.util.concatenate(mesh_list)
        bnd_box = concat_mesh.bounding_box

        # Calculate current volume fraction based on bounding box volume
        current_vf = volume_total_current / bnd_box.volume
        print(f"Iteration {iteration + 1}: Current volume fraction = {current_vf}")

        # Check if the current volume fraction is within the tolerance range
        if abs(current_vf - vf_target) <= tolerance:
            print(f"Target volume fraction achieved: {current_vf}")
            break

        # Calculate the translation factor incrementally
        translate_factor = (current_vf - vf_target) / current_vf
        if translate_factor < 0 or translate_factor > 1:
            print(
                "Warning: Translate factor out of valid range. Adjusting to fit within [0, 1]."
            )
            translate_factor = max(0, min(1, translate_factor))

        translate_factor = (1 - translate_factor) ** (1 / 3)

        # Calculate the centroid of the bounding box
        center_bnd_box = bnd_box.centroid

        # Translate each mesh based on the calculated factor
        for mesh in mesh_list:
            direction_vector = mesh.bounding_box.centroid - center_bnd_box
            distance_from_center = np.linalg.norm(direction_vector)

            if distance_from_center > 0:
                normalized_direction = direction_vector / distance_from_center
            else:
                normalized_direction = np.zeros_like(direction_vector)

            # Scale translation distance based on the relative distance from the center
            scaled_translate_distance = distance_from_center * (1 - translate_factor)
            translation_vector = normalized_direction * scaled_translate_distance
            mesh.apply_translation(translation_vector)

        # Recalculate the total volume and volume fraction after translation
        volume_total_current = sum(mesh.volume for mesh in mesh_list)
        concat_mesh = trimesh.util.concatenate(mesh_list)
        bnd_box = concat_mesh.bounding_box
        new_vf = volume_total_current / bnd_box.volume
        print(f"Volume fraction after iteration {iteration + 1} = {new_vf}")

    # Export the reduced mesh list
    export_mesh_list(mesh_list, file_path, "reduced_vf_")
