import trimesh

# Define the parameters of the cylinder
diameter = 50  # mm
radius = diameter / 2
height = 50  # mm
center_x, center_y, center_z = 0, height / 2 + 10, 0

# Create a cylinder mesh
cylinder = trimesh.creation.cylinder(radius=radius, height=height, sections=36)

cylinder.apply_translation([center_x, center_y, center_z])

# Define the file path
file_path = "cylinder.stl"

# Export the cylinder mesh to an STL file
cylinder.export(file_path)

print(f"STL file saved to {file_path}")
