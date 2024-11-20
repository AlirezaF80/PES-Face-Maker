import os
import glob
from tqdm import tqdm

PES_VERSION = "pes21_dlc7"
FACES_FOLDER_PATH = r'D:\Games Installers\PES 2021\Datapacks_21\DLC7\Asset\model\character\face\real'

BASE_PATH = "D:/Projects/Pycharm Projects/PES-Face-Maker"
EXPORTING_TEXTURES_FOLDER_PATH = f'{BASE_PATH}/ExportingTextures'
EXPORT_FOLDER_PATH = f'{BASE_PATH}/texture_exports/{PES_VERSION}'
os.makedirs(EXPORT_FOLDER_PATH, exist_ok=True)


def ftex_to_png(image_path, export_path):
    # Run ftex_to_png.py with the provided image_path and export_path
    command = f'python "{EXPORTING_TEXTURES_FOLDER_PATH}/ftex_to_png.py" "{image_path}" "{export_path}"'
    os.system(command)


# Find face_bsm_alp.ftex files in each folder
face_folders = glob.glob(os.path.join(FACES_FOLDER_PATH, '*'))
for face_folder in tqdm(face_folders):
    face_id = os.path.basename(face_folder)
    face_bsm_alp_file = os.path.join(face_folder, 'sourceimages', '#windx11', 'face_bsm_alp.ftex')
    if not os.path.exists(face_bsm_alp_file):
        print(f'No face_bsm_alp.ftex found for face `{face_id}`')
        continue

    export_path = os.path.join(EXPORT_FOLDER_PATH, face_id + '.png')
    ftex_to_png(face_bsm_alp_file, export_path)
    print(f'Exported face `{face_id}` to {export_path}')
