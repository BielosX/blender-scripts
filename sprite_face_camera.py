import bpy
import bmesh
import math

from mathutils import Vector, Matrix

def modify_vertices_position(mesh, matrix):
    bmesh_plane = bmesh.new()
    bmesh_plane.from_mesh(mesh)

    for vertex in bmesh_plane.verts:
        vertex.co = matrix @ vertex.co

    bmesh_plane.to_mesh(mesh)
    bmesh_plane.free()
    mesh.update()

def camera_direction(camera):
    average_point = Vector((0.0, 0.0, 0.0))
    for point in camera.data.view_frame():
        average_point += point
    average_point /= 4.0
    camera_location = Vector(camera.location)
    direction = average_point - camera_location
    direction.normalize()
    return direction

def det(vec1, vec2):
    return vec1[0] * vec2[1] - vec2[0] * vec1[1]

def project_xy(vec):
    xy_vec = vec.xy
    if xy_vec.length == 0.0:
        return Vector((1.0, 0.0))
    xy_vec.normalize()
    return xy_vec

def project_xz(vec):
    xz_vec = vec.xz
    if xz_vec.length == 0:
        return Vector((1.0, 0.0))
    xz_vec.normalize()
    return xz_vec

class SpriteFaceCameraOperator(bpy.types.Operator):
    bl_idname = "object.sprite_face_camera_operator"
    bl_label = "Sprite Face Camera"
    
    @classmethod
    def poll(cls, context):
        selected_objects = context.selected_objects
        if len(selected_objects) == 2:
            first = selected_objects[0]
            second = selected_objects[1]
            if first.type == "CAMERA" or second.type == "CAMERA":
                if first.type == "MESH":
                    if len(first.data.vertices) == 4:
                        return True
                if second.type == "MESH":
                    if len(second.data.vertices) == 4:
                        return True
        return False
    
    def execute(self, context):
        selected_objects = context.selected_objects
        first = selected_objects[0]
        second = selected_objects[1]
        camera = first if first.type == "CAMERA" else second
        plane = first if first.type == "MESH" else second
        expected_plane_normal = -camera_direction(camera)
        plane_normal = plane.data.polygon_normals[0].vector
        
        expected_normal_xy = project_xy(expected_plane_normal)
        plane_normal_xy = project_xy(plane_normal)
        xy_dot = expected_normal_xy.dot(plane_normal_xy)
        xy_det = det(expected_normal_xy, plane_normal_xy)
        
        xy_angle = math.atan2(xy_det, xy_dot)
        
        expected_normal_xz = project_xz(expected_plane_normal)
        plane_normal_xz = project_xz(plane_normal)
        xz_dot = expected_normal_xz.dot(plane_normal_xz)
        xz_det = det(expected_normal_xz, plane_normal_xz)
        
        xz_angle = math.atan2(xz_det, xz_dot)
        
        mat_rot_z = Matrix.Rotation(-xy_angle, 4, 'Z')
        mat_rot_y = Matrix.Rotation(xz_angle, 4, 'Y')
        
        rot_matrix = mat_rot_z @ mat_rot_y
        
        modify_vertices_position(plane.data, rot_matrix)
        
        return {"FINISHED"}
    
def sprite_face_camera(self, context):
    self.layout.operator(
        SpriteFaceCameraOperator.bl_idname, text=SpriteFaceCameraOperator.bl_label
    )
    
    
def register():
    bpy.utils.register_class(SpriteFaceCameraOperator)
    bpy.types.VIEW3D_MT_object.append(sprite_face_camera)
    
if __name__ == "__main__":
    register()