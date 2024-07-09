import gmsh
import os


def main():
    # Initialize the Gmsh API
    gmsh.initialize()

    # Create a new model
    gmsh.model.add("imported_model")

    # Import the STL file
    gmsh.merge("c.stl")

    # Synchronize the model
    gmsh.model.occ.synchronize()

    # Define the meshing parameters
    gmsh.option.setNumber("Mesh.Algorithm", 1)  # 3D meshing algorithm
    gmsh.option.setNumber("Mesh.CharacteristicLengthMin", 0.1)
    gmsh.option.setNumber("Mesh.CharacteristicLengthMax", 0.1)

    # Generate the 3D mesh (tetrahedral mesh)
    gmsh.model.mesh.generate(3)

    # Save the mesh to ABAQUS (.inp) and VTK (.vtk) formats
    output_files = ["tetrahedral_mesh.inp", "tetrahedral_mesh.vtk"]

    for output_file in output_files:
        gmsh.write(output_file)
        print(f"Mesh saved to: {os.path.abspath(output_file)}")

    # Finalize the Gmsh API
    gmsh.finalize()


if __name__ == "__main__":
    main()
