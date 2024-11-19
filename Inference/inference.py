from tensorflow.keras import models
import numpy as np
from deepface import DeepFace
import trimesh

from DimensionReduction.reduce_pca_run import PCA_MODEL_PATH

BASE_PATH = "D:/Projects/Pycharm Projects/PES-Face-Maker"
DEFAULT_FACE_PATH = f'{BASE_PATH}/assets/default_face.obj'
INFERENCE_FOLDER_PATH = f"{BASE_PATH}/Inference"
MODEL_PATH = f"{INFERENCE_FOLDER_PATH}/model_epoch_99.keras"

model = models.load_model(MODEL_PATH)
# Load the PCA model
pca_model = np.load(PCA_MODEL_PATH, allow_pickle=True).item()

IMAGE_PATH = f"{INFERENCE_FOLDER_PATH}/ali karimi est.jpg"

embedding = DeepFace.represent(IMAGE_PATH, model_name="Facenet512", max_faces=1, align=True, expand_percentage=10)
embedding = np.array(embedding[0]['embedding']).reshape(1, -1)

predicted_pca_embed = model.predict(embedding)
predicted_pca_embed /= 50

reconstructed_embedding = pca_model.inverse_transform(predicted_pca_embed)
print(reconstructed_embedding)
print(reconstructed_embedding.shape)

# Load the default face and set the reconstructed embedding as the new vertices
default_face = trimesh.load(DEFAULT_FACE_PATH, process=False)

# Get the difference between the default face and the reconstructed face
diff = reconstructed_embedding.reshape(-1, 3) - default_face.vertices
print(diff)

default_face.vertices = reconstructed_embedding.reshape(-1, 3) + diff * 3
default_face.export(f"{INFERENCE_FOLDER_PATH}/reconstructed_face.obj")
