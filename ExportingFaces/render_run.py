import os
import subprocess
from glob import glob
from tqdm import tqdm

base_path = "D:/Projects/Pycharm Projects/PES-Face-Maker"
script_path = f'{base_path}/ExportingFaces/render.py'
blender_path = 'C:/Program Files/Blender Foundation/Blender 2.83/blender.exe'

blend_file_path = f'{base_path}/ExportingFaces/render_2.83.blend'

render_output_path = f"{base_path}/face_images/pes21_dt36"
faces_folder_path = 'D:/Games Installers/PES 2021/DT36_21/Asset/model/character/face/real'
already_exported_faces = set(map(lambda x: os.path.basename(x).replace('.png', ''), glob(f'{render_output_path}/*.png')))
all_faces_to_export = set(glob(os.path.join(faces_folder_path, '*')))
not_yet_rendered_faces = list(filter(lambda x: os.path.basename(x) not in already_exported_faces, all_faces_to_export))

for face_path in tqdm(not_yet_rendered_faces):
    face_id = os.path.basename(face_path)

    command = (
        f'"{blender_path}" "{blend_file_path}" -b -P "{script_path}" -- '
        f'--face_path "{face_path}" '
        f'--output_dir "{render_output_path}"'
    )

    subprocess.run(command, shell=True)
    print(f'Rendered face `{face_id}`')