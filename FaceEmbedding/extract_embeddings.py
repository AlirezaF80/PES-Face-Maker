import os
import numpy as np
from tqdm import tqdm
import glob
from deepface import DeepFace
import cv2
from multiprocessing import Pool, cpu_count

EXPAND_PERCENT = 10
EMBED_MODEL_NAME = 'Facenet512'
DETECTOR_BACKEND = 'opencv'

PES_VERSION = "pes21_dt36"
EMBEDDINGS_EXPORT_FOLDER = f"D:/Projects/Pycharm Projects/PES-Face-Maker/embeddings/{PES_VERSION}"
os.makedirs(EMBEDDINGS_EXPORT_FOLDER, exist_ok=True)

face_images_folder = f"D:/Projects/Pycharm Projects/PES-Face-Maker/face_images/{PES_VERSION}"
face_images = glob.glob(os.path.join(face_images_folder, "*.png"))
face_image_ids = set(map(lambda x: os.path.basename(x).replace('.png', ''), face_images))

obj_exports_folder = f"D:/Projects/Pycharm Projects/PES-Face-Maker/obj_exports/{PES_VERSION}"
obj_export_files = glob.glob(os.path.join(obj_exports_folder, "*.obj"))
obj_export_ids = set(map(lambda x: os.path.basename(x).replace('.obj', ''), obj_export_files))

faces_to_extract_embeddings = face_image_ids.intersection(obj_export_ids)

bad_faces_ids = set()
face_region_sum = np.zeros(4)


def process_face(face_id):
    embedding_path = os.path.join(EMBEDDINGS_EXPORT_FOLDER, f"{face_id}.npy")
    if os.path.exists(embedding_path):
        return None  # Skip if embedding already exists

    try:
        embedding_objs = DeepFace.represent(
            img_path=os.path.join(face_images_folder, f"{face_id}.png"),
            detector_backend=DETECTOR_BACKEND,
            align=True,
            expand_percentage=EXPAND_PERCENT,
            model_name=EMBED_MODEL_NAME
        )

        if len(embedding_objs) != 1:
            return face_id  # Bad face (multiple/no faces detected)

        embedding = np.array(embedding_objs[0]['embedding'])
        face_region = embedding_objs[0]['facial_area']
        np.save(embedding_path, embedding)
        return face_region
    except Exception as e:
        tqdm.write(f"Error processing {face_id}: {str(e)}")
        return face_id  # Mark as bad face


def crop_and_retry(face_id, avg_face_region):
    img = cv2.imread(os.path.join(face_images_folder, f"{face_id}.png"))
    x, y, w, h = [int(coord) for coord in avg_face_region]
    face_img = img[y:y + h, x:x + w]
    cropped_img_path = os.path.join(face_images_folder, f"{face_id}_cropped.png")
    cv2.imwrite(cropped_img_path, face_img)

    try:
        embedding_objs = DeepFace.represent(
            img_path=cropped_img_path,
            align=True,
            expand_percentage=EXPAND_PERCENT,
            model_name=EMBED_MODEL_NAME,
            enforce_detection=False
        )
        if len(embedding_objs) == 1:
            embedding = np.array(embedding_objs[0]['embedding'])
            embedding_path = os.path.join(EMBEDDINGS_EXPORT_FOLDER, f"{face_id}.npy")
            np.save(embedding_path, embedding)
    except Exception as e:
        tqdm.write(f"Retry failed for {face_id}: {str(e)}")


def main():
    global face_region_sum
    with Pool(2) as pool:
        results = list(
            tqdm(pool.imap(process_face, faces_to_extract_embeddings), total=len(faces_to_extract_embeddings)))

    face_regions = [res for res in results if isinstance(res, dict)]
    bad_faces = [res for res in results if isinstance(res, str)]

    if len(face_regions) == 0:
        print("Not enough faces to calculate average face region.")

    # Average face region calculation
    for region in face_regions:
        face_region_sum += np.array([region['x'], region['y'], region['w'], region['h']])
    avg_face_region = face_region_sum / len(face_regions) if face_regions else np.zeros(4)
    print(f"Avg face region: {avg_face_region}")

    # Process bad faces
    for face_id in tqdm(bad_faces):
        crop_and_retry(face_id, avg_face_region)

    print("Embeddings extracted successfully.")


if __name__ == "__main__":
    main()
