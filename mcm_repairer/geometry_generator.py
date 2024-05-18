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
