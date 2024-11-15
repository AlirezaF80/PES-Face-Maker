import os
from typing import Optional

import numpy as np
from sklearn.decomposition import PCA
import trimesh


def load_obj_file(file_path):
    """
    Load an OBJ file and extract vertex coordinates.
    """
    mesh = trimesh.load(file_path, process=False)
    if not isinstance(mesh, trimesh.Trimesh):
        raise ValueError(f"{file_path} is not a valid 3D mesh.")
    return mesh.vertices


def load_all_obj_files(folder_path):
    """
    Load all OBJ files in a folder and stack their vertex coordinates.
    """
    all_vertices = []
    obj_files = [f for f in os.listdir(folder_path) if f.endswith('.obj')]

    for obj_file in obj_files:
        file_path = os.path.join(folder_path, obj_file)
        vertices = load_obj_file(file_path)
        all_vertices.append(vertices)

    # Ensure all models have the same number of vertices
    n_vertices = all_vertices[0].shape[0]
    for v in all_vertices:
        if v.shape[0] != n_vertices:
            raise ValueError("All models must have the same number of vertices.")

    # Convert list to a 2D numpy array of shape (n_models, n_vertices * 3)
    return np.array(all_vertices).reshape(len(all_vertices), -1)


def get_pca_of_all_models(data, variance_threshold: Optional[float]):
    """
    Apply PCA on the stacked models to reduce dimensions and preserve a given variance.
    """
    # Apply PCA
    pca = PCA(n_components=variance_threshold) if variance_threshold is not None else PCA()
    pca.fit_transform(data)

    # Print the number of components available
    print(f"Number of components: {len(pca.explained_variance_ratio_)}")

    return pca


if __name__ == "__main__":
    # Path to the folder containing OBJ files
    obj_folder_path = "D:/Projects/Pycharm Projects/PES-Face-Maker/obj_exports/pes21_dt36"

    # Load all OBJ files and stack vertex coordinates
    all_vertices = load_all_obj_files(obj_folder_path)

    # Apply PCA on the stacked data
    pca_model = get_pca_of_all_models(all_vertices, variance_threshold=0.95)

    # Save PCA Model for later use
    np.save("pca_model.npy", pca_model)
