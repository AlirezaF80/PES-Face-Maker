import glob
import os

import cv2
import numpy as np
from sklearn.mixture import GaussianMixture
from tqdm import tqdm

from ExportingTextures.create_texture_pca import PCA_MODEL_PATH, TEXTURE_SIZE

PES_VERSIONS = ["pes21_dlc1", "pes21_dlc2", "pes21_dlc3", "pes21_dlc4", "pes21_dlc5", "pes21_dlc6",
                "pes21_dlc7"]

BASE_PATH = "D:/Projects/Pycharm Projects/PES-Face-Maker"
EXPORTING_TEXTURES_FOLDER_PATH = os.path.join(BASE_PATH, "ExportingTextures")
TEXTURES_PATH = os.path.join(BASE_PATH, "texture_exports")

texture_paths = []
for pes_version in PES_VERSIONS:
    texture_paths += glob.glob(os.path.join(TEXTURES_PATH, pes_version, "*.png"))

# Loading and processing textures in batches
all_textures = []
for i, texture_path in tqdm(enumerate(texture_paths), desc="Reading textures"):
    batch_textures = []
    texture = cv2.imread(texture_path)
    texture = cv2.resize(texture, (TEXTURE_SIZE, TEXTURE_SIZE))
    batch_textures.append(texture)

    batch_textures = np.array(batch_textures).reshape(len(batch_textures), -1)  # Flatten each texture
    all_textures.extend(batch_textures)
print("All textures loaded.")

pca = np.load(PCA_MODEL_PATH, allow_pickle=True).item()
print("PCA model loaded.")

# Fit GMM to PCA-transformed training data
pca_coefficients = pca.transform(all_textures)
print("Fitting GMM...")

gmm = GaussianMixture(n_components=5, covariance_type='full')
gmm.fit(pca_coefficients)

print("GMM fitted.")

# Save GMM model
np.save(os.path.join(EXPORTING_TEXTURES_FOLDER_PATH, "gmm_texture_model.npy"), gmm)
