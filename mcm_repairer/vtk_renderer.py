import vtk
import trimesh
import vtk


class VTKScene:
    def __init__(self):
        self.renderer = vtk.vtkRenderer()
        self.render_window = vtk.vtkRenderWindow()
        self.render_window.AddRenderer(self.renderer)
        self.render_window_interactor = vtk.vtkRenderWindowInteractor()
        self.render_window_interactor.SetRenderWindow(self.render_window)
        self.actors = []

        self.renderer.SetBackground(0.1, 0.2, 0.4)  # Background color

    def trimesh_to_vtk(self, trimesh_mesh):
        points = vtk.vtkPoints()
        for vertex in trimesh_mesh.vertices:
            points.InsertNextPoint(vertex[0], vertex[1], vertex[2])

        cells = vtk.vtkCellArray()
        for face in trimesh_mesh.faces:
            cells.InsertNextCell(3)
            cells.InsertCellPoint(face[0])
            cells.InsertCellPoint(face[1])
            cells.InsertCellPoint(face[2])

        poly_data = vtk.vtkPolyData()
        poly_data.SetPoints(points)
        poly_data.SetPolys(cells)

        if trimesh_mesh.vertex_normals is not None:
            normals = vtk.vtkFloatArray()
            normals.SetNumberOfComponents(3)
            normals.SetName("Normals")
            for normal in trimesh_mesh.vertex_normals:
                normals.InsertNextTuple(normal)
            poly_data.GetPointData().SetNormals(normals)

        if trimesh_mesh.visual.kind == "vertex":
            colors = vtk.vtkUnsignedCharArray()
            colors.SetNumberOfComponents(3)
            colors.SetName("Colors")
            for color in trimesh_mesh.visual.vertex_colors:
                colors.InsertNextTuple3(color[0], color[1], color[2])
            poly_data.GetPointData().SetScalars(colors)

        return poly_data

    def add_mesh(
        self,
        trimesh_mesh,
        color=(1, 1, 1),
        opacity=1.0,
        show_edges=False,
        edge_color=(0, 0, 0),
    ):
        poly_data = self.trimesh_to_vtk(trimesh_mesh)
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(poly_data)

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(color)
        actor.GetProperty().SetOpacity(opacity)

        if show_edges:
            actor.GetProperty().SetEdgeVisibility(1)
            actor.GetProperty().SetEdgeColor(edge_color)

        self.actors.append(actor)
        self.renderer.AddActor(actor)
        self.render_window.Render()

    def remove_mesh(self, actor):
        self.renderer.RemoveActor(actor)
        self.actors.remove(actor)
        self.render_window.Render()

    def start_interaction(self):
        self.render_window.Render()
        self.render_window_interactor.Initialize()
        self.render_window_interactor.Start()
