from OCC.Core.BRep import BRep_Builder
from OCC.Core.BRepBuilderAPI import (
    BRepBuilderAPI_MakeFace,
    BRepBuilderAPI_MakePolygon,
    BRepBuilderAPI_MakeSolid,
    BRepBuilderAPI_Sewing,
)
from OCC.Core.gp import gp_Pnt
from OCC.Core.TopoDS import TopoDS_Compound
from OCC.Core.TopoDS import TopoDS_Shape, TopoDS_Solid, topods_Shell
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_FACE
from OCC.Core.TopoDS import topods_Face
from OCC.Core.BRep import BRep_Tool
from OCC.Core.TopLoc import TopLoc_Location


def create_faces_from_polygons(
    faces: list[list[int]], vertices: list[tuple[float, float, float]]
) -> TopoDS_Compound:
    compound = TopoDS_Compound()
    builder = BRep_Builder()
    builder.MakeCompound(compound)
    polygon = BRepBuilderAPI_MakePolygon()
    for face in faces:
        polygon = BRepBuilderAPI_MakePolygon()
        for index in face:
            point = gp_Pnt(*vertices[index])
            polygon.Add(point)
        polygon.Close()
        face = BRepBuilderAPI_MakeFace(polygon.Wire())
        builder.Add(compound, face.Face())
    return compound


def create_solid_from_shell(shell: TopoDS_Shape) -> TopoDS_Solid:
    solid_maker = BRepBuilderAPI_MakeSolid()
    solid_maker.Add(topods_Shell(shell))
    solid = solid_maker.Solid()
    return solid


def create_solid_from_polygons(
    faces: list[list[int]], vertices: list[tuple[float, float, float]]
) -> TopoDS_Solid:
    faces_compound = create_faces_from_polygons(faces, vertices)
    sewed_shell = sew_compound_faces(faces_compound)
    solid = create_solid_from_shell(sewed_shell)
    return solid


def sew_compound_faces(faces_compound: TopoDS_Compound) -> TopoDS_Shape:
    sewer = BRepBuilderAPI_Sewing()
    sewer.Add(faces_compound)
    sewer.Perform()
    sewed_shell = sewer.SewedShape()
    return sewed_shell


def convert_shape_to_mesh(shape, linear_deflection=0.01, angular_deflection=0.5):
    mesh = BRepMesh_IncrementalMesh(
        shape,
        linear_deflection,
        False,
        angular_deflection,
        False,
    )
    mesh.Perform()

    if not mesh.IsDone():
        raise Exception("Meshing failed.")

    return mesh


def create_compound(shape_list):
    compound = TopoDS_Compound()
    builder = BRep_Builder()
    builder.MakeCompound(compound)
    for solid in shape_list:
        builder.Add(compound, solid)
    return compound


def extract_vertices_and_faces_from_mesh(shape):
    vertices = []
    faces = []

    exp = TopExp_Explorer(shape, TopAbs_FACE)
    while exp.More():
        face = topods_Face(exp.Current())
        triangulation = BRep_Tool.Triangulation(face, TopLoc_Location())

        if triangulation is None:
            exp.Next()
            continue

        # Extract vertices
        for i in range(1, triangulation.NbNodes() + 1):
            node = triangulation.Node(i)
            vertices.append([node.X(), node.Y(), node.Z()])

        # Extract faces
        for i in range(1, triangulation.NbTriangles() + 1):
            triangle = triangulation.Triangle(i)
            n1, n2, n3 = triangle.Get()
            faces.append([n1 - 1, n2 - 1, n3 - 1])  # 0-based indexing for trimesh

        exp.Next()

    return vertices, faces
