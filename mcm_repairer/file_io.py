from trimesh import Geometry, load_mesh, util
from os.path import isfile
from OCC.Core.StlAPI import StlAPI_Writer
from mcm_repairer.utility import add_prefix_if_exists

# TODO: replace trimesh with OCC.Core.RWStl in order to remove trimesh and scipy. OCC.Core.RWStl does not split a mesh so a mesh splitter method needs no be implemented.


def load_stl(file_path: str) -> list[Geometry]:
    if not isfile(file_path):
        raise ValueError(f"File does not exist: {file_path}")
    mesh = load_mesh(file_path, "stl")

    if isinstance(mesh, list):
        return mesh
    else:
        return mesh.split(only_watertight=True)  # type: ignore


def export_to_stl(shape, file_path, ascii_mode=False):
    writer = StlAPI_Writer()
    writer.SetASCIIMode(ascii_mode)
    if writer.Write(shape, file_path):
        print(f"Successfully exported to {file_path}")
    else:
        raise ValueError(f"Failed to export to {file_path}")


def export_mesh_list(mesh_list, file_path, file_name_prefix):
    combined_filtered_mesh = util.concatenate(mesh_list)
    export_path = add_prefix_if_exists(file_path, file_name_prefix)
    combined_filtered_mesh.export(export_path)  # type: ignore
    print("exported to " + file_path)
