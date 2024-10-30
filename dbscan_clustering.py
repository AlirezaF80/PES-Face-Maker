import glob

from numpy import unique
from sklearn.cluster import DBSCAN
from tqdm import tqdm

from objParser import import_obj


def get_vertices_distance(vertices_1, vertices_2):
    diff = [vertices_1[i] - vertices_2[i] for i in range(len(vertices_1))]
    power = [d ** 2 for d in diff]
    return sum(power) ** 0.5


if __name__ == '__main__':
    all_objs = []
    print("Importing objects...")
    for obj_file in tqdm(glob.glob('./obj_exports/pes21_dt36/*.obj')[:100]):
        vertices = []
        for v in import_obj(obj_file).vertices:
            vertices.extend([v.x, v.y, v.z])
        all_objs.append(vertices)
    # print some differences between objects
    distances = []
    for i in range(len(all_objs)):
        for j in range(i + 1, len(all_objs)):
            # print(f'{i} and {j} have {get_vertices_distance(all_objs[i], all_objs[j])}')
            distances.append(get_vertices_distance(all_objs[i], all_objs[j]))
    # graph the distances
    import matplotlib.pyplot as plt
    plt.hist(distances, bins=100)
    plt.show()

    print("Calculating distances...")
    model = DBSCAN(eps=0.1, min_samples=5, metric=get_vertices_distance)
    print("Clustering...")
    yhat = model.fit_predict(all_objs)
    print("Clustering done!")
    clusters = unique(yhat)
    print(f"Found {len(clusters)} clusters")
    unique_objs = []
    for cluster in clusters:
        unique_objs.append([all_objs[i] for i, c in enumerate(yhat) if c == cluster])
    # print(unique_objs)
