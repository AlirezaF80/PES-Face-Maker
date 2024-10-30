import os
import sys
import random
import bpy


def import_face(fpk_path):
    bpy.ops.extract_scene.fpk(filepath=fpk_path, face_high_fmdl=True, hair_high_fmdl=True, oral_fmdl=True,
                              pes_diff_bin=True, fixMeshsmooth=True)


def change_to_textured_shading():
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.viewport_shade = 'TEXTURED'


def remove_everything_but(objs_to_keep):
    for obj in bpy.data.objects:
        if obj.name not in objs_to_keep:
            bpy.data.objects.remove(obj)


def join_all_objs_with(obj_name):
    select_object_as_active(obj_name)
    select_all_objects()
    bpy.ops.object.join()


def select_all_objects():
    bpy.ops.object.select_all(action='SELECT')


def deselect_all_objects():
    bpy.ops.object.select_all(action='DESELECT')


def get_object_by_name(name):
    return bpy.data.objects[name]


def set_object_select_by_name(name, select=True):
    get_object_by_name(name).select = select


def select_object_as_active(obj_name):
    active_obj = get_object_by_name(obj_name)
    bpy.context.scene.objects.active = active_obj


def remove_doubles():
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.remove_doubles()
    bpy.ops.object.editmode_toggle()


def import_obj_file(file_path):
    bpy.ops.import_scene.obj(filepath=file_path, split_mode='OFF')


def export_selected_to_obj(export_path):
    bpy.ops.export_scene.obj(filepath=export_path, use_selection=True, use_materials=False,
                             keep_vertex_order=True)


def find_next_face(faces_path, export_path):
    import glob
    all_faces_ids = set(os.listdir(faces_path))
    exported_objs = list(map(os.path.basename, glob.glob(export_path + '/*.obj')))
    exported_ids = set(map(lambda x: x.replace('.obj', ''), exported_objs))
    remaining_ids = all_faces_ids - exported_ids
    if len(remaining_ids) == 0:
        print('All faces exported!')
        return None
    return random.choice(list(remaining_ids))


def clear_unused_files():
    bpy.ops.primary.operator(face_opname='clr_file')


def copy_vertices_from_to(from_obj_name, to_obj_name, from_uv_name, to_uv_name):
    bpy.context.scene.cpy_uv_loc_uv_distance_threshold = 0.0001
    from_obj = get_object_by_name(from_obj_name)
    to_obj = get_object_by_name(to_obj_name)
    bpy.context.scene.cpy_uv_loc_src = from_obj
    bpy.context.scene.cpy_uv_loc_trg = to_obj
    bpy.context.scene.cpy_uv_loc_src_uv_name = from_uv_name
    bpy.context.scene.cpy_uv_loc_trg_uv_name = to_uv_name
    bpy.ops.object.copy_vert_loc_by_uv()


def main(face_path, export_path, default_face_path):
    objs_to_keep = ['mesh_id_face_0', 'mesh_id_face_2', 'mesh_id_hair_0']
    fpk_path = os.path.join(face_path, '#Win/face.fpk')
    import_face(fpk_path)
    remove_everything_but(objs_to_keep)
    join_all_objs_with('mesh_id_face_0')
    remove_doubles()
    face_0 = get_object_by_name('mesh_id_face_0')
    face_0.modifiers.new("Subsurf", 'SUBSURF')
    face_0.modifiers['Subsurf'].subdivision_type = 'SIMPLE'
    face_0.modifiers['Subsurf'].levels = 2
    bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Subsurf")
    import_obj_file(default_face_path)
    select_all_objects()
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    copy_vertices_from_to('mesh_id_face_0', 'default_face', 'UVMap', 'UVMap')
    remove_everything_but(['default_face'])
    select_all_objects()
    export_selected_to_obj(export_path)
    print("Exported face to " + export_path)
    clear_unused_files()

# face_path = "D:/Games Installers/PES 2021/DT36_21/Asset/model/character/face/real/557"
# export_path = "D:/Projects/Pycharm Projects/PES-Face-Maker/obj_exports/pes21_dt36/557.obj"
# default_face_path = "D:/Projects/Pycharm Projects/PES-Face-Maker/assets/avg_head.obj"

# main(face_path, export_path, default_face_path)

if __name__ == "__main__":
    # Use sys.argv to parse command-line arguments manually
    args = sys.argv

    # Initialize variables for arguments
    face_path = None
    export_path = None
    default_face_path = None

    # Parse command-line arguments
    for i in range(len(args)):
        if args[i] == '--face_path':
            face_path = args[i + 1]
        elif args[i] == '--export_path':
            export_path = args[i + 1]
        elif args[i] == '--default_face_path':
            default_face_path = args[i + 1]

    # Ensure all arguments are provided
    if face_path and export_path and default_face_path:
        main(face_path, export_path, default_face_path)
    else:
        print("Error: Missing required arguments --face_path, --export_path, or --default_face_path")
