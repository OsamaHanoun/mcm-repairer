from trimesh import Geometry, load_mesh
from os.path import isfile
from OCC.Core.StlAPI import StlAPI_Writer

# TODO: replace trimesh with OCC.Core.RWStl in order to remove trimesh and scipy. OCC.Core.RWStl does not split a mesh so a mesh splitter method needs no be implemented.


def load_stl(file_path: str) -> list[Geometry]:
    if not isfile(file_path):
        raise ValueError(f"File does not exist: {file_path}")
    mesh: Geometry = load_mesh(file_path, "stl")
    meshes: list[Geometry] = mesh.split(only_watertight=True)
    return meshes


def export_to_stl(shape, filename, ascii_mode=False):
    writer = StlAPI_Writer()
    writer.SetASCIIMode(ascii_mode)
    if writer.Write(shape, filename):
        print(f"Successfully exported to {filename}")
    else:
        raise ValueError(f"Failed to export to {filename}")
