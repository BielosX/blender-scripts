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


class GeometryToOriginOperator(bpy.types.Operator):
    bl_idname = "object._my_geometry_to_origin_operator"
    bl_label = "My Geometry To Origin"
    
    @classmethod
    def poll(cls, context):
        active_obj = context.active_object
        return active_obj is not None
    
    def execute(self, context):
        active = context.active_object
        active_mesh = active.data
        
        active_origin = Vector(active.location)
        
        average_point = Vector((0.0, 0.0, 0.0))
        
        for vertex in active_mesh.vertices:
            coord_vector = Vector(vertex.co)
            average_point += coord_vector
            
        average_point /= len(active_mesh.vertices)
        
        diff = active_origin - average_point
        
        modify_vertices_position(active_mesh, diff)
        
        return {'FINISHED'}
    
def geometry_to_origin(self, context):
    self.layout.operator(GeometryToOriginOperator.bl_idname, text=GeometryToOriginOperator.bl_label)
    
def register():
    bpy.utils.register_class(GeometryToOriginOperator)
    bpy.types.VIEW3D_MT_object.append(geometry_to_origin)
    
if __name__ == "__main__":
    register()