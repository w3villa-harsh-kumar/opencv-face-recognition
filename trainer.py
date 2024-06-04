# import os
# import cv2
# import numpy as np
# from PIL import Image

# recognizer = cv2.face.LBPHFaceRecognizer_create()
# path = "dataset"

# def get_images_with_ids(path):
#     image_paths = [os.path.join(path,f) for f in os.listdir(path)]
#     faces = []
#     ids = []
#     for single_image_path in image_paths:
#         faceImg = Image.open(single_image_path).convert("L")
#         faceNp = np.array(faceImg, np.uint8)
#         Id = int(os.path.split(single_image_path)[-1].split(".")[1])
#         print(Id)
#         faces.append(faceNp)
#         ids.append(Id)
#         cv2.imshow("training", faceNp)
#         cv2.waitKey(10)

#     return np.array(ids), faces

# ids, faces = get_images_with_ids(path)
# recognizer.train(faces, ids)
# recognizer.save("recognizer/trainingdata.yml")
# cv2.destroyAllWindows()


import os
import cv2
import numpy as np
from PIL import Image, ImageEnhance

recognizer = cv2.face.LBPHFaceRecognizer_create()
path = "dataset"

def preprocess_image(image):
    image = cv2.equalizeHist(image)  # Histogram equalization
    return cv2.resize(image, (200, 200))  # Resize to standard size

def augment_image(image):
    images = [image]
    # Add flipped images
    images.append(cv2.flip(image, 1))
    return images

def get_images_with_ids(path):
    image_paths = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.jpg')]
    faces = []
    ids = []
    for single_image_path in image_paths:
        faceImg = Image.open(single_image_path).convert("L")
        faceNp = np.array(faceImg, np.uint8)
        faceNp = preprocess_image(faceNp)  # Preprocess the image
        Id = int(os.path.split(single_image_path)[-1].split(".")[1])
        for augmented_face in augment_image(faceNp):  # Augment the image
            faces.append(augmented_face)
            ids.append(Id)
        cv2.imshow("training", faceNp)
        cv2.waitKey(10)

    return np.array(ids), faces

ids, faces = get_images_with_ids(path)
recognizer.train(faces, ids)
recognizer.save("recognizer/trainingdata.yml")
cv2.destroyAllWindows()
