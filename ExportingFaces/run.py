import os
from tqdm import tqdm
import glob
import subprocess

base_path = "D:/Projects/Pycharm Projects/PES-Face-Maker"
script_path = f'{base_path}/ExportingFaces/export_face_to_obj.py'
blender_path = 'C:/Program Files/Blender Foundation/Blender/blender.exe'

faces_folder_path = 'D:/Games Installers/PES 2021/DT36_21/Asset/model/character/face/real'
export_folder_path = f'{base_path}/obj_exports/pes21_dt36'
default_face_path = f'{base_path}/assets/default_face.obj'

for face_path in tqdm(glob.glob(os.path.join(faces_folder_path, '*'))):
    face_id = os.path.basename(face_path)
    export_path = os.path.join(export_folder_path, face_id + '.obj')
    print(f'Exporting face `{face_id}` to {export_path}')

    # command = (
    #     f'"{blender_path}" -b -P "{script_path}" -- '
    #     f'--face_path "{face_path}" '
    #     f'--export_path "{export_path}" '
    #     f'--default_face_path "{default_face_path}"'
    # )
    # print(command)
    # os.system(command)

    command = (
        f'"{blender_path}" -b -P "{script_path}" -- '
        f'--face_path "{face_path}" '
        f'--export_path "{export_path}" '
        f'--default_face_path "{default_face_path}"'
    )

    subprocess.run(command, shell=True)
    break  # Remove this break to process all faces
