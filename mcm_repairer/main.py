from mcm_repairer.file_io import load_stl
from mcm_repairer.geometry_generator import create_solid_from_polygons


def repair_model(file_path):
    meshes = load_stl(file_path)
    solids = []

    for mesh in meshes:
        solid = create_solid_from_polygons(mesh.faces, mesh.vertices)
        solids.append(solid)
