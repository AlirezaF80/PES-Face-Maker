import os
import glob
import numpy as np
from sklearn.decomposition import PCA
from tqdm import tqdm
import cv2
import time

PES_VERSIONS = ["pes21_dlc1", "pes21_dlc2", "pes21_dlc3", "pes21_dlc4", "pes21_dlc5", "pes21_dlc6", "pes21_dlc7"]

BASE_PATH = "D:/Projects/Pycharm Projects/PES-Face-Maker"
TEXTURES_PATH = os.path.join(BASE_PATH, "texture_exports")

texture_paths = []
for pes_version in PES_VERSIONS:
    texture_paths += glob.glob(os.path.join(TEXTURES_PATH, pes_version, "*.png"))

# Load all textures
TEXTURE_SIZE = 256
all_textures = []
for texture_path in tqdm(texture_paths, desc="Loading textures"):
    texture = cv2.imread(texture_path)
    texture = cv2.resize(texture, (TEXTURE_SIZE, TEXTURE_SIZE))
    all_textures.append(texture)
# Convert list to a 2D numpy array of shape (n_textures, n_pixels * 3)
all_textures = np.array(all_textures).reshape(len(all_textures), -1)
print("Loaded all textures.")

pca_start_time = time.time()
# Apply PCA
pca = PCA(n_components=0.95)
pca.fit_transform(all_textures)
print(f"Number of components: {len(pca.explained_variance_ratio_)}")
print(f"PCA took {time.time() - pca_start_time:.2f} seconds.")

# Save PCA model
np.save(os.path.join(BASE_PATH, "pca_texture_model.npy"), pca)