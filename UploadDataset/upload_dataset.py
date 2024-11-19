# Uploading PCA reduced data, as well as all the embeddings
import json

import datasets
import pandas as pd
import os
import numpy as np
import glob

HF_TOKEN = os.getenv("HF_TOKEN")
HF_REPO_NAME = "AlirezaF138/PES-Face-Maker"

BASE_PATH = "D:/Projects/Pycharm Projects/PES-Face-Maker"

PES_VERSIONS = [
    "pes21_dt36",
    "pes21_dlc1",
    "pes21_dlc2",
    "pes21_dlc3",
    "pes21_dlc4",
    "pes21_dlc5",
    "pes21_dlc6",
    "pes21_dlc7"
]

data = []
for pes_version in PES_VERSIONS:
    EMBEDDINGS_PATH = f"{BASE_PATH}/embeddings/{pes_version}/"
    PCA_OUTPUTS_PATH = f"{BASE_PATH}/pca_outputs/{pes_version}/"

    embedding_files = glob.glob(os.path.join(EMBEDDINGS_PATH, "*.npy"))
    embedding_ids = set(map(lambda x: os.path.basename(x).replace('.npy', ''), embedding_files))

    pca_files = glob.glob(os.path.join(PCA_OUTPUTS_PATH, "*.npy"))
    pca_ids = set(map(lambda x: os.path.basename(x).replace('.npy', ''), pca_files))

    common_ids = embedding_ids.intersection(pca_ids)

    for face_id in common_ids:
        embedding = list(np.load(os.path.join(EMBEDDINGS_PATH, f"{face_id}.npy")))
        pca_embedding = list(np.load(os.path.join(PCA_OUTPUTS_PATH, f"{face_id}.npy")))
        data.append([embedding, pca_embedding, face_id, "Facenet512", pes_version])

df = pd.DataFrame(data, columns=["embedding", "pca_embedding", "face_id", "model_name", "pes_version"])
dataset = datasets.Dataset.from_pandas(df)

# Upload the dataset to HuggingFace
dataset.push_to_hub(HF_REPO_NAME, private=True, token=HF_TOKEN)
