import bpy
import bmesh

from mathutils import Vector


def modify_vertices_position(mesh, vec):
    bmesh_plane = bmesh.new()
    bmesh_plane.from_mesh(mesh)

    for vertex in bmesh_plane.verts:
        vertex.co += vec

    bmesh_plane.to_mesh(mesh)
    bmesh_plane.free()
    mesh.update()


def average_point(mesh):
    point = Vector((0.0, 0.0, 0.0))

    for vertex in mesh.vertices:
        coord_vector = Vector(vertex.co)
        point += coord_vector

    point /= len(mesh.vertices)
    return point


class GeometryToOriginOperator(bpy.types.Operator):
    bl_idname = "object._my_geometry_to_origin_operator"
    bl_label = "My Geometry To Origin"

    @classmethod
    def poll(cls, context):
        active_obj = context.active_object
        return active_obj is not None and active_obj.type == "MESH"

    def execute(self, context):
        active = context.active_object
        active_mesh = active.data
        active_origin = Vector(active.location)
        diff = active_origin - (active.matrix_basis @ average_point(active_mesh))
        modify_vertices_position(active_mesh, diff)
        return {"FINISHED"}


class OriginToGeometryOperator(bpy.types.Operator):
    bl_idname = "object._my_origin_to_geometry_operator"
    bl_label = "My Origin To Geometry"

    @classmethod
    def poll(cls, context):
        active_obj = context.active_object
        return active_obj is not None and active_obj.type == "MESH"

    def execute(self, context):
        active = context.active_object
        active_mesh = active.data
        active_origin = Vector(active.location)
        from_origin_to_average = (
            active.matrix_basis @ average_point(active_mesh)
        ) - active_origin
        active_origin += from_origin_to_average
        active.location = (active_origin.x, active_origin.y, active_origin.z)
        from_average_to_origin = -from_origin_to_average
        modify_vertices_position(active_mesh, from_average_to_origin)
        return {"FINISHED"}


class OriginTo3DCursorOperator(bpy.types.Operator):
    bl_idname = "object._my_origin_to_3d_cursor_operator"
    bl_label = "My Origin To 3D Cursor"

    @classmethod
    def poll(cls, context):
        active_obj = context.active_object
        return active_obj is not None and active_obj.type == "MESH"

    def execute(self, context):
        cursor_location = context.scene.cursor.location
        active = context.active_object
        active_origin = Vector(active.location)
        origin_to_cursor = cursor_location - active_origin
        active_origin += origin_to_cursor
        active.location = (active_origin.x, active_origin.y, active_origin.z)
        modify_vertices_position(active.data, -origin_to_cursor)
        return {"FINISHED"}


def geometry_to_origin(self, context):
    self.layout.operator(
        GeometryToOriginOperator.bl_idname, text=GeometryToOriginOperator.bl_label
    )


def origin_to_geometry(self, context):
    self.layout.operator(
        OriginToGeometryOperator.bl_idname, text=OriginToGeometryOperator.bl_label
    )


def origin_to_3d_cursor(self, context):
    self.layout.operator(
        OriginTo3DCursorOperator.bl_idname, text=OriginTo3DCursorOperator.bl_label
    )


def register():
    bpy.utils.register_class(GeometryToOriginOperator)
    bpy.types.VIEW3D_MT_object.append(geometry_to_origin)
    bpy.utils.register_class(OriginToGeometryOperator)
    bpy.types.VIEW3D_MT_object.append(origin_to_geometry)
    bpy.utils.register_class(OriginTo3DCursorOperator)
    bpy.types.VIEW3D_MT_object.append(origin_to_3d_cursor)


if __name__ == "__main__":
    register()
