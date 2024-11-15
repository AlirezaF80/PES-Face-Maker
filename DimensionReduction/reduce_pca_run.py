import numpy as np
import glob
import os

import trimesh
from tqdm import tqdm


def load_obj_file(file_path):
    """
    Load an OBJ file and extract vertex coordinates.
    """
    mesh = trimesh.load(file_path, process=False)
    if not isinstance(mesh, trimesh.Trimesh):
        raise ValueError(f"{file_path} is not a valid 3D mesh.")
    return mesh.vertices

def reduce_dimensions(data, pca_model):
    """
    Reduce dimensions of the data using a pre-trained PCA model.
    """
    data_reduced = pca_model.transform(data)
    return data_reduced


def reconstruct_data(data_reduced, pca_model):
    """
    Reconstruct the original data from the reduced data using a pre-trained PCA model.
    """
    data_reconstructed = pca_model.inverse_transform(data_reduced)
    return data_reconstructed


PES_VERSION = "pes21_dt36"

PCA_MODEL_PATH = f"D:/Projects/Pycharm Projects/PES-Face-Maker/DimensionReduction/pca_model.npy"
PCA_OUTPUTS_PATH = f"D:/Projects/Pycharm Projects/PES-Face-Maker/pca_outputs/{PES_VERSION}/"
os.makedirs(PCA_OUTPUTS_PATH, exist_ok=True)
FACE_MODELS_PATH = f"D:/Projects/Pycharm Projects/PES-Face-Maker/obj_exports/{PES_VERSION}/"

if __name__ == '__main__':
    # Load PCA Model
    pca_model = np.load(PCA_MODEL_PATH, allow_pickle=True).item()

    face_ids = set(map(lambda x: os.path.basename(x).replace('.obj', ''), glob.glob(f'{FACE_MODELS_PATH}/*.obj')))
    # Load data
    for face_id in tqdm(face_ids):
        file_path = os.path.join(FACE_MODELS_PATH, f"{face_id}.obj")
        data = load_obj_file(file_path)
        data = data.reshape(1, -1)
        if data.shape[1] != 6759:
            tqdm.write(f"Skipping {face_id}.obj due to incorrect number of vertices")
            continue

        # Reduce dimensions
        data_reduced = reduce_dimensions(data, pca_model)

        # Save reduced data
        np.save(os.path.join(PCA_OUTPUTS_PATH, f"{face_id}.npy"), data_reduced)

        # Reconstruct data
        # data_reconstructed = reconstruct_data(data_reduced, pca_model)

        # Measure the reconstruction error
        # reconstruction_error = np.mean((data - data_reconstructed) ** 2)
