import sys

import bpy
import os


def import_face(face_path):
    bpy.ops.extract_scene.fpk(filepath=face_path, face_high_fmdl=True, hair_high_fmdl=True, oral_fmdl=True,
                              pes_diff_bin=True, fixMeshsmooth=True)


def clear_face_unused_files():
    bpy.ops.primary.operator(face_opname='clr_file')


def select_all_objects():
    bpy.ops.object.select_all(action='SELECT')


def deselect_all_objects():
    bpy.ops.object.select_all(action='DESELECT')


def get_object_by_name(name):
    return bpy.data.objects[name]


def set_object_select_by_name(name, select=True):
    get_object_by_name(name).select = select


def remove_objects(*obj_names):
    for obj in bpy.data.objects:
        if obj.name in obj_names:
            bpy.data.objects.remove(obj)


def main(face_id, face_path, output_dir):
    import_face(face_path)
    remove_objects('mesh_id_face_3', 'mesh_id_face_1')

    file_name = face_id + ".png"
    bpy.context.scene.render.filepath = os.path.join(output_dir, file_name)
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    # Use sys.argv to parse command-line arguments manually
    args = sys.argv

    # Initialize variables for arguments
    face_path = None
    output_dir = None

    # Parse command-line arguments
    for i in range(len(args)):
        if args[i] == '--face_path':
            face_path = args[i + 1]
        elif args[i] == '--output_dir':
            output_dir = args[i + 1]

    face_id = os.path.basename(face_path)
    fpk_path = os.path.join(face_path, "#Win", "face.fpk")

    # Ensure all arguments are provided
    if face_path and output_dir:
        main(face_id, fpk_path, output_dir)
    else:
        print("Error: Missing required arguments --face_path or --output_dir")


