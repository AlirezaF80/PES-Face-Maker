# Uploading PCA reduced data, as well as all the embeddings
import json

import datasets
import pandas as pd
import os
import numpy as np
import glob

HF_TOKEN = os.getenv("HF_TOKEN")
HF_REPO_NAME = "AlirezaF138/PES-Face-Maker"

PES_VERSION = "pes21_dt36"
EMBEDDINGS_PATH = f"D:/Projects/Pycharm Projects/PES-Face-Maker/embeddings/{PES_VERSION}"
PCA_OUTPUTS_PATH = f"D:/Projects/Pycharm Projects/PES-Face-Maker/pca_outputs/{PES_VERSION}"

embedding_files = glob.glob(os.path.join(EMBEDDINGS_PATH, "*.npy"))
embedding_ids = set(map(lambda x: os.path.basename(x).replace('.npy', ''), embedding_files))

pca_files = glob.glob(os.path.join(PCA_OUTPUTS_PATH, "*.npy"))
pca_ids = set(map(lambda x: os.path.basename(x).replace('.npy', ''), pca_files))

common_ids = embedding_ids.intersection(pca_ids)

# Each row should be a face embedding, a PCA reduced embedding, and the face id, and also the face model used, and pes version
data = []
for face_id in common_ids:
    embedding = list(np.load(os.path.join(EMBEDDINGS_PATH, f"{face_id}.npy")))
    pca_embedding = list(np.load(os.path.join(PCA_OUTPUTS_PATH, f"{face_id}.npy")))
    data.append([embedding, pca_embedding, face_id, "Facenet", PES_VERSION])

df = pd.DataFrame(data, columns=["embedding", "pca_embedding", "face_id", "model_name", "pes_version"])
dataset = datasets.Dataset.from_pandas(df)

# Upload the dataset to HuggingFace
dataset.push_to_hub(HF_REPO_NAME, private=True, token=HF_TOKEN)
