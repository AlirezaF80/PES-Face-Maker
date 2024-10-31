import os
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

    for obj_file in obj_files[:200]:
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


def apply_pca_on_models(data, variance_threshold=0.95):
    """
    Apply PCA on the stacked models to reduce dimensions and preserve a given variance.
    """
    # Apply PCA
    pca = PCA()
    data_pca = pca.fit_transform(data)

    # Calculate cumulative variance
    cumulative_variance = np.cumsum(pca.explained_variance_ratio_)

    # Determine the number of components to retain
    n_components = np.argmax(cumulative_variance >= variance_threshold) + 1

    # Apply PCA with the optimal number of components
    pca = PCA(n_components=n_components)
    data_reduced = pca.fit_transform(data)
    data_reconstructed = pca.inverse_transform(data_reduced)

    print(
        f"Optimal number of components: {n_components}, Cumulative variance: {cumulative_variance[n_components - 1]:.2f}")
    return data_reduced, data_reconstructed, pca


def save_reconstructed_obj(data, original_file_path, output_file_path):
    """
    Save reconstructed vertex coordinates as an OBJ file.
    """
    mesh = trimesh.load(original_file_path, process=False)
    mesh.vertices = data
    mesh.export(output_file_path)


if __name__ == "__main__":
    # Path to the folder containing OBJ files
    obj_folder_path = "D:/Projects/Pycharm Projects/PES-Face-Maker/obj_exports/pes21_dt36"

    # Load all OBJ files and stack vertex coordinates
    all_vertices = load_all_obj_files(obj_folder_path)

    # Apply PCA on the stacked data
    reduced_data, reconstructed_data, pca_model = apply_pca_on_models(all_vertices, variance_threshold=0.95)

    # Save the reconstructed data for the first model as a sample
    first_file_path = os.path.join(obj_folder_path, os.listdir(obj_folder_path)[0])
    print(first_file_path)
    output_file_path = "reconstructed_sample.obj"
    save_reconstructed_obj(reconstructed_data[0].reshape(-1, 3), first_file_path, output_file_path)

    print("Sample reconstructed OBJ saved.")
