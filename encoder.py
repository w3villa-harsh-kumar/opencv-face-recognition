import cv2
import numpy as np
import face_recognition
import os
import csv
import json


encodingPath = 'encoded.csv'
path = 'Images'
images = []
names = []
List = os.listdir(path)


def load_images_from_folder(folder):
    images = []
    for filename in os.listdir(folder):
        img_path = os.path.join(folder, filename)
        if os.path.isfile(img_path):
            img = cv2.imread(img_path)
            if img is not None:
                images.append(img)
    return images

def encode_images(images):
    encode_list = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodeImg = face_recognition.face_encodings(img)
        if encodeImg:
            encode_list.append(encodeImg[0])
    return encode_list



def encode_folders(path):
    person_names = []
    all_encodings = []
    for person_folder in os.listdir(path):
        person_folder_path = os.path.join(path, person_folder)


        if os.path.isdir(person_folder_path):
            images = load_images_from_folder(person_folder_path)
            encodings = encode_images(images)

            print("Encoading in array form of image",encodings)

            if encodings:
                avg_encoding = np.mean(np.array(encodings), axis=0)
                person_names.append(person_folder)
                all_encodings.append(avg_encoding)
    return person_names, all_encodings


def record_encodings(names, encodings):
    with open(encodingPath, 'a+', newline='\n') as file:
        file.seek(0)
        records = csv.reader(file, delimiter=',')
        nameList = [row[0] for row in records]

        fieldnames = ['Name', 'Encoding']

        writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=',')

        if file.tell() == 0:
            writer.writeheader()
            
        for name, encoding in zip(names, encodings):
            if name not in nameList:
                encoding_list = encoding.tolist()
                writer.writerow({'Name': name, 'Encoding': encoding_list})
                # print("encoding_list",encoding_list)
                print(f"{name} Recorded!")

            else:
                print(f"{name} Already Recorded!")


# Main process
print("Encoding images from folders...")
names, encodeList = encode_folders(path)
record_encodings(names, encodeList)
print("Encoding Completed.")