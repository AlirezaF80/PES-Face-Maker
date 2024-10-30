import os

import tqdm

# the path should be absolute
script_path = 'D:/.../export_face_to_obj.py'
blender_path = 'C:/Program Files/Blender Foundation/Blender 2.79/blender.exe'


for _ in tqdm.tqdm(range(2123)):
    os.system(f'{blender_path} -b -P "{script_path}"')

