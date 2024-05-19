from trimesh import Geometry, load_mesh
from os.path import isfile
from OCC.Core.StlAPI import StlAPI_Writer

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
