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
    obj_files.sort()  # Ensure consistent order

    for obj_file in obj_files:
        file_path = os.path.join(folder_path, obj_file)
        vertices = load_obj_file(file_path)
        all_vertices.append(vertices.flatten())

    # Ensure all models have the same number of vertices
    n_vertices = all_vertices[0].shape[0]
    for v in all_vertices:
        if v.shape[0] != n_vertices:
            raise ValueError("All models must have the same number of vertices.")

    # Convert list to a 2D numpy array of shape (n_samples, n_features)
    return np.array(all_vertices), obj_files


def compute_mean_shape(data):
    """
    Compute the mean shape from the data.
    """
    mean_shape = np.mean(data, axis=0)
    return mean_shape

def center_data(data, mean_shape):
    """
    Center the data by subtracting the mean shape.
    """
    centered_data = data - mean_shape
    return centered_data


def perform_pca(data_centered, n_components=None, variance_threshold=0.95):
    """
    Perform PCA on the centered data.
    """
    pca = PCA(n_components=n_components)
    pca.fit(data_centered)

    if n_components is None:
        cumulative_variance = np.cumsum(pca.explained_variance_ratio_)
        n_components = np.argmax(cumulative_variance >= variance_threshold) + 1
        pca = PCA(n_components=n_components)
        pca.fit(data_centered)

    components = pca.components_
    explained_variance = pca.explained_variance_ratio_

    return pca, components, explained_variance


def generate_shape_keys(components, mean_shape, n_vertices):
    """
    Generate shape keys from PCA components.
    """
    shape_keys = []
    for i, component in enumerate(components):
        shape_key = mean_shape + component
        shape_key = shape_key.reshape(n_vertices, 3)
        shape_keys.append(shape_key)
    return shape_keys


def save_obj(vertices, faces, file_path):
    """
    Save the vertices and faces to an OBJ file.
    """
    with open(file_path, 'w') as f:
        for v in vertices:
            f.write(f"v {v[0]} {v[1]} {v[2]}\n")
        for face in faces:
            f.write(f"f {face[0]+1} {face[1]+1} {face[2]+1}\n")


if __name__ == "__main__":
    # Path to the folder containing OBJ files
    obj_folder_path = "D:/Projects/Pycharm Projects/PES-Face-Maker/obj_exports/pes21_dt36"

    # Load all OBJ files and get vertex coordinates and file names
    all_data, obj_files = load_all_obj_files(obj_folder_path)

    n_samples, n_features = all_data.shape
    n_vertices = n_features // 3  # Each vertex has 3 coordinates

    # Compute the mean shape
    mean_shape = compute_mean_shape(all_data)

    # Center the data
    data_centered = center_data(all_data, mean_shape)

    # Perform PCA
    pca_model, components, explained_variance = perform_pca(data_centered, variance_threshold=0.9)

    # Generate shape keys
    shape_keys = generate_shape_keys(components, mean_shape, n_vertices)

    # Load faces from one of the original models (assuming all have same topology)
    sample_mesh = trimesh.load(os.path.join(obj_folder_path, obj_files[0]), process=False)
    faces = sample_mesh.faces

    # Save the mean shape
    mean_shape_vertices = mean_shape.reshape(n_vertices, 3)
    save_obj(mean_shape_vertices, faces, os.path.join("D:/Projects/Pycharm Projects/PES-Face-Maker/shape_keys", "mean_shape.obj"))

    # Save the shape keys
    for i, shape_key_vertices in enumerate(shape_keys):
        file_name = f"shape_key_{i+1}.obj"
        save_obj(shape_key_vertices, faces, os.path.join("D:/Projects/Pycharm Projects/PES-Face-Maker/shape_keys", file_name))
        print(f"Saved {file_name}")

    print("All shape keys and mean shape have been saved.")
