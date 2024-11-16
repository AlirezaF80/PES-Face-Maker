# [{'embedding': [-0.05050182342529297, -0.9010071754455566, -0.17350313067436218, 0.86864173412323, 0.0914328321814537, -1.3870288133621216, -1.4202637672424316, 0.14234250783920288, 0.17867660522460938, -0.07706819474697113, 0.8668437600135803, 0.6347960829734802, 1.7690105438232422, -2.313408374786377, -0.44569745659828186, -0.22023768723011017, 1.3411602973937988, -0.45692890882492065, -1.5666613578796387, -0.07602599263191223, 0.6863913536071777, -0.3871488571166992, 0.18964123725891113, -0.024854399263858795, 0.178909033536911, -0.4546140432357788, 0.3105645477771759, 2.7548608779907227, 2.099091053009033, 1.0098648071289062, -0.7333143949508667, 0.14254552125930786, -2.507420063018799, -1.0142574310302734, 0.5623575448989868, -0.7936892509460449, -0.5088950395584106, -0.6308638453483582, -2.1446869373321533, 0.48389971256256104, -1.4333728551864624, 0.9004138112068176, 0.9743683338165283, 1.2126176357269287, 1.4423662424087524, -0.640066921710968, 2.6189491748809814, -0.4607822299003601, 0.5629397630691528, -0.8354417085647583, -1.3759812116622925, 0.1043681651353836, -1.2914458513259888, 1.2521836757659912, -1.565609097480774, 0.44564881920814514, 0.4831390678882599, 0.41184908151626587, -0.7327470183372498, 1.5738385915756226, -0.21094870567321777, 0.8718019127845764, 1.4151005744934082, -0.14900463819503784, -0.6287632584571838, 2.1503360271453857, 0.09927231073379517, 2.1557023525238037, -0.11078017950057983, -1.8307030200958252, -0.7150385975837708, 1.84505295753479, -0.9787312150001526, 1.2750049829483032, 0.2774231433868408, 1.1644303798675537, -0.03236864507198334, 0.3463723659515381, -0.11565034836530685, -1.4151164293289185, -0.9493045210838318, -0.38175368309020996, -0.9207619428634644, -0.35639673471450806, -0.3481758236885071, -2.07446551322937, -0.6189640164375305, -2.279412031173706, -0.07779170572757721, -1.1902599334716797, 0.8136568665504456, -0.18886923789978027, 0.3453015089035034, -0.64678555727005, 0.04758525267243385, 2.354123115539551, -1.1667962074279785, 0.290170818567276, 0.9672227501869202, -1.6305761337280273, 1.5448518991470337, 0.6059477925300598, 1.383378505706787, -1.5769808292388916, 0.7323992252349854, 1.795947551727295, -1.4849684238433838, -0.9100627899169922, 0.40225717425346375, -1.029809594154358, 1.148056983947754, -0.004850663244724274, 0.4549797773361206, -0.9576342105865479, 0.8632305264472961, 2.1312718391418457, -1.2578808069229126, 0.2824174463748932, -1.3385940790176392, 1.316064715385437, 0.6453765034675598, 0.1837494671344757, 0.38441920280456543, -0.1707596331834793, 0.651251494884491, 0.17421644926071167, -0.19343498349189758, -2.577100992202759], 'facial_area': {'x': 208, 'y': 182, 'w': 613, 'h': 613, 'left_eye': (598, 442), 'right_eye': (421, 430)}, 'face_confidence': np.float64(0.9)}]
import os
import numpy as np
from tqdm import tqdm
import glob
from deepface import DeepFace
import cv2

EXPAND_PERCENT = 20
EMBED_MODEL_NAME = 'Facenet'
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

# common face ids
faces_to_extract_embeddings = face_image_ids.intersection(obj_export_ids)

bad_faces_ids = set()
# Used to get sum of all face regions detected, then averaged out to be used for bad faces later
face_region_sum = np.zeros(4)
for face_id in tqdm(faces_to_extract_embeddings):
    embedding_objs = DeepFace.represent(
        img_path=os.path.join(face_images_folder, f"{face_id}.png"),
        detector_backend=DETECTOR_BACKEND,
        align=True,
        expand_percentage=EXPAND_PERCENT,
        model_name=EMBED_MODEL_NAME
    )

    if len(embedding_objs) != 1:
        tqdm.write(f"Multiple/No faces detected in {face_id}.png")
        bad_faces_ids.add(face_id)
        continue
    embedding = np.array(embedding_objs[0]['embedding'])
    face_region = embedding_objs[0]['facial_area']
    face_region_sum += np.array([face_region['x'], face_region['y'], face_region['w'], face_region['h']])
    embedding_path = os.path.join(EMBEDDINGS_EXPORT_FOLDER, f"{face_id}.npy")
    np.save(embedding_path, embedding)

avg_face_region = face_region_sum / (len(faces_to_extract_embeddings) - len(bad_faces_ids))
print(f"Avg face region: {avg_face_region}")

for face_id in tqdm(bad_faces_ids):
    # Crop the face region from the image
    img = cv2.imread(os.path.join(face_images_folder, f"{face_id}.png"))
    x, y, w, h = avg_face_region
    x, y, w, h = int(x), int(y), int(w), int(h)
    face_img = img[y:y + h, x:x + w]
    cropped_img_path = os.path.join(face_images_folder, f"{face_id}_cropped.png")
    cv2.imwrite(cropped_img_path, face_img)

    # Extract embeddings from the cropped face
    embedding_objs = DeepFace.represent(
        img_path=cropped_img_path,
        align=True,
        expand_percentage=EXPAND_PERCENT,
        model_name=EMBED_MODEL_NAME,
        enforce_detection=False
    )

    if len(embedding_objs) != 1:
        tqdm.write(f"Multiple/No faces detected in {face_id}_cropped.png")
        continue
    embedding = np.array(embedding_objs[0]['embedding'])
    embedding_path = os.path.join(EMBEDDINGS_EXPORT_FOLDER, f"{face_id}.npy")
    np.save(embedding_path, embedding)

print("Embeddings extracted successfully.")
