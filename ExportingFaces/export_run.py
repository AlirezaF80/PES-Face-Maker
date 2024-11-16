import os
from tqdm import tqdm
import glob
import subprocess

BASE_PATH = "D:/Projects/Pycharm Projects/PES-Face-Maker"
SCRIPT_PATH = f'{BASE_PATH}/ExportingFaces/export_face_to_obj.py'
BLENDER_PATH = 'C:/Program Files/Blender Foundation/Blender/blender.exe'

FACES_FOLDER_PATH = r'D:\Games Installers\PES 2021\Datapacks_21\DLC7\Asset\model\character\face\real'
EXPORT_FOLDER_PATH = f'{BASE_PATH}/obj_exports/pes21_dlc7'
DEFAULT_FACE_PATH = f'{BASE_PATH}/assets/default_face.obj'

os.makedirs(EXPORT_FOLDER_PATH, exist_ok=True)

already_exported_faces = set(map(lambda x: os.path.basename(x).replace('.obj', ''), glob.glob(f'{EXPORT_FOLDER_PATH}/*.obj')))
all_faces_to_export = set(glob.glob(os.path.join(FACES_FOLDER_PATH, '*')))
not_yet_exported_faces = list(filter(lambda x: os.path.basename(x) not in already_exported_faces, all_faces_to_export))
for face_path in tqdm(not_yet_exported_faces):
    face_id = os.path.basename(face_path)
    export_path = os.path.join(EXPORT_FOLDER_PATH, face_id + '.obj')
    print(f'Exporting face `{face_id}` to {export_path}')

    command = (
        f'"{BLENDER_PATH}" -b -P "{SCRIPT_PATH}" -- '
        f'--face_path "{face_path}" '
        f'--export_path "{export_path}" '
        f'--default_face_path "{DEFAULT_FACE_PATH}"'
    )

    subprocess.run(command, shell=True)
