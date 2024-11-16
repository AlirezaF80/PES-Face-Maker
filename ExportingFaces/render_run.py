import os
import subprocess
from glob import glob
from tqdm import tqdm

BASE_PATH = "D:/Projects/Pycharm Projects/PES-Face-Maker"
SCRIPT_PATH = f'{BASE_PATH}/ExportingFaces/render.py'
BLENDER_PATH = 'C:/Program Files/Blender Foundation/Blender 2.83/blender.exe'
BLEND_FILE_PATH = f'{BASE_PATH}/ExportingFaces/render_2.83.blend'

FACES_FOLDER_PATH = r'D:\Games Installers\PES 2021\Datapacks_21\DLC1\Asset\model\character\face\real'
RENDER_OUTPUT_PATH = f"{BASE_PATH}/face_images/pes21_dlc1"
os.makedirs(RENDER_OUTPUT_PATH, exist_ok=True)

already_exported_faces = set(map(lambda x: os.path.basename(x).replace('.png', ''), glob(f'{RENDER_OUTPUT_PATH}/*.png')))
all_faces_to_export = set(glob(os.path.join(FACES_FOLDER_PATH, '*')))
not_yet_rendered_faces = list(filter(lambda x: os.path.basename(x) not in already_exported_faces, all_faces_to_export))

for face_path in tqdm(not_yet_rendered_faces):
    face_id = os.path.basename(face_path)

    command = (
        f'"{BLENDER_PATH}" "{BLEND_FILE_PATH}" -b -P "{SCRIPT_PATH}" -- '
        f'--face_path "{face_path}" '
        f'--output_dir "{RENDER_OUTPUT_PATH}"'
    )

    subprocess.run(command, shell=True)
    print(f'Rendered face `{face_id}`')