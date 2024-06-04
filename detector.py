# import cv2
# import numpy as np
# import os
# import sqlite3

# facedetect = cv2.CascadeClassifier("haarcascade/haarcascade_frontalface_default.xml")
# cam = cv2.VideoCapture(0)
# recognizer = cv2.face.LBPHFaceRecognizer_create()
# recognizer.read("recognizer/trainingdata.yml")

# def getProfile(id):
#     conn=sqlite3.connect("sqlite.db")
#     cursor=conn.execute("SELECT * FROM students WHERE Id=?", (Id,))
#     profile=None
#     for row in cursor:
#         profile=row
#     conn.close()
#     return profile


# while(True):
#     ret,img=cam.read()
#     gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
#     faces=facedetect.detectMultiScale(gray,1.3,5)
#     for(x,y,w,h) in faces:
#         cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
#         Id,conf=recognizer.predict(gray[y:y+h,x:x+w])
#         profile=getProfile(Id)
#         print(profile)
#         if(profile != None):
#             cv2.putText(img, "Name : "+str(profile[1]), (x,y+h+20),cv2.FONT_HERSHEY_COMPLEX, 1,(0,255,127),2)
#             cv2.putText(img, "Age : "+str(profile[2]), (x,y+h+45),cv2.FONT_HERSHEY_COMPLEX, 1,(0,255,127),2)
            

#     cv2.imshow("Face",img)
#     if(cv2.waitKey(1)==ord('q')):
#         break

# cam.release()
# cv2.destroyAllWindows()




import cv2
import numpy as np
import os
import sqlite3

facedetect = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
cam = cv2.VideoCapture(0)
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("recognizer/trainingdata.yml")

def getProfile(Id):
    conn = sqlite3.connect("sqlite.db")
    cursor = conn.execute("SELECT * FROM students WHERE Id=?", (Id,))
    profile = None
    for row in cursor:
        profile = row
    conn.close()
    return profile

confidence_threshold = 50  # Set a confidence threshold for predictions

while True:
    ret, img = cam.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = facedetect.detectMultiScale(gray, 1.3, 5)
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        Id, conf = recognizer.predict(gray[y:y+h, x:x+w])
        if conf < confidence_threshold:
            profile = getProfile(Id)
            if profile is not None:
                cv2.putText(img, f"Name: {profile[1]}", (x, y + h + 20), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 127), 2)
                cv2.putText(img, f"Age: {profile[2]}", (x, y + h + 45), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 127), 2)
                cv2.putText(img, f"Conf: {int(conf)}", (x, y + h + 70), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 127), 2)
            else:
                cv2.putText(img, "Unknown", (x, y + h + 20), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
        else:
            cv2.putText(img, "Unknown", (x, y + h + 20), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("Face", img)
    if cv2.waitKey(1) == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()

