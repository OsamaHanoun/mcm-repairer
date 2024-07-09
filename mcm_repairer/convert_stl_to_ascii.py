from mcm_repairer.file_io import load_stl, export_mesh_list
import trimesh


def convert(file_path):
    # Load a mesh from a file
    mesh_list = load_stl(file_path)
    scene = trimesh.Scene()

    # Add each mesh to the scene
    for mesh in mesh_list:
        scene.add_geometry(mesh)

    # Export the scene to an ASCII STL file
    output_file_path = "combined_output_meshes.stl"
    scene.export(output_file_path, file_type="stl", ascii=True)
