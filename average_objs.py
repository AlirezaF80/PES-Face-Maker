import glob

from tqdm import tqdm

from objParser import import_obj

if __name__ == '__main__':
    default_face = import_obj('./assets/default_face.obj')
    avg_face = default_face.__copy__()
    objects_included = 0
    for obj_file in tqdm(glob.glob('./obj_exports/pes21_dt36/*.obj')):
        obj = import_obj(obj_file)
        if len(obj.vertices) != len(default_face.vertices):
            print(f'{obj_file} has {len(obj.vertices)} vertices, but {len(default_face.vertices)} expected')
            continue
        objects_included += 1
        avg_face.vertices = [avg_face.vertices[i] + obj.vertices[i] for i in range(len(avg_face.vertices))]
    avg_face.vertices = [v / objects_included for v in avg_face.vertices]
    avg_face.faces = []

    # write obj to avg_face.obj
    with open('./obj_results/avg_face.obj', 'w') as f:
        f.write(avg_face.to_obj_str() + default_face._faces_to_str())