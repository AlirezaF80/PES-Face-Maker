import os
import glob
import numpy as np
from sklearn.decomposition import IncrementalPCA
from tqdm import tqdm
import cv2
import time

PES_VERSIONS = ["pes21_dt36", "pes21_dlc1", "pes21_dlc2", "pes21_dlc3", "pes21_dlc4", "pes21_dlc5", "pes21_dlc6", "pes21_dlc7"]

BASE_PATH = "D:/Projects/Pycharm Projects/PES-Face-Maker"
EXPORTING_TEXTURES_FOLDER_PATH = os.path.join(BASE_PATH, "ExportingTextures")
TEXTURES_PATH = os.path.join(BASE_PATH, "texture_exports")

texture_paths = []
for pes_version in PES_VERSIONS:
    texture_paths += glob.glob(os.path.join(TEXTURES_PATH, pes_version, "*.png"))

# Constants
TEXTURE_SIZE = 256
BATCH_SIZE = 512  # Number of textures to process per batch

# IncrementalPCA
pca = IncrementalPCA()

# Loading and processing textures in batches
all_textures = []
for i in tqdm(range(0, len(texture_paths), BATCH_SIZE), desc="Processing textures"):
    batch_paths = texture_paths[i:i + BATCH_SIZE]
    batch_textures = []

    for texture_path in batch_paths:
        texture = cv2.imread(texture_path)
        texture = cv2.resize(texture, (TEXTURE_SIZE, TEXTURE_SIZE))
        batch_textures.append(texture)

    batch_textures = np.array(batch_textures).reshape(len(batch_textures), -1)  # Flatten each texture
    pca.partial_fit(batch_textures)  # Incrementally fit PCA
    all_textures.extend(batch_textures)

all_textures = np.array(all_textures)
print("All textures loaded and PCA trained.")

# Save PCA model
np.save(os.path.join(EXPORTING_TEXTURES_FOLDER_PATH, "pca_texture_model.npy"), pca)

print("PCA model saved.")

# Transform textures and reconstruct some for error analysis
pca_start_time = time.time()
n_reconstructions = 5
compressed_textures = pca.transform(all_textures[:n_reconstructions])
reconstructed_textures = pca.inverse_transform(compressed_textures)
print(f"PCA and reconstruction completed in {time.time() - pca_start_time:.2f} seconds.")

# Calculate errors
reconstructed_textures = reconstructed_textures.reshape(n_reconstructions, TEXTURE_SIZE, TEXTURE_SIZE, 3)
for i, texture in enumerate(reconstructed_textures):
    error = np.mean((all_textures[i] - reconstructed_textures[i].reshape(-1)) ** 2)
    print(f"Reconstruction {i} error: {error}")
