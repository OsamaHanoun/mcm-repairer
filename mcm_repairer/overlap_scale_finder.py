import trimesh


def has_overlap(mesh1, mesh2):
    # Check if two meshes intersect
    return not mesh1.intersection(mesh2).is_empty


def scale_mesh(mesh, scale_factor):
    scaled_mesh = mesh.copy()
    scaled_mesh.apply_scale(scale_factor)
    translation_vector = mesh.centroid - scaled_mesh.centroid
    scaled_mesh.apply_translation(translation_vector)
    return scaled_mesh


def find_no_overlap(mesh1, mesh2, min_volume=1.0, tolerance=1e-3):
    low = min_volume / mesh1.volume
    high = (mesh1.volume - mesh1.intersection(mesh2).volume) / mesh1.volume

    best_scale = None
    low_overlap = False

    while high - low > tolerance:
        if low_overlap:
            break

        mid = (low + high) / 2
        scaled_mesh = scale_mesh(mesh1, mid)
        overlap = has_overlap(scaled_mesh, mesh2)

        if overlap:
            high = mid
        else:
            low = mid
            low_overlap = overlap
            best_scale = mid

    if best_scale is not None:
        return best_scale, scale_mesh(mesh1, best_scale)
    return None, None
