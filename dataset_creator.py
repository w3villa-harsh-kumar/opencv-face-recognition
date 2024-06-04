
import cv2
import numpy as np
import os

faceDetect=cv2.CascadeClassifier('haarcascade/haarcascade_frontalface_default.xml')
cam = cv2.VideoCapture(0)

import sqlite3

def create_table():
    conn = sqlite3.connect("sqlite.db")
    cursor = conn.cursor()
    
    # Create table
    cursor.execute('''CREATE TABLE IF NOT EXISTS students (
                        ID INTEGER PRIMARY KEY,
                        Name TEXT NOT NULL,
                        Age INTEGER NOT NULL
                      )''')
    
    conn.commit()
    conn.close()

def insertOrUpdate(Id, Name, Age):
    conn = sqlite3.connect("sqlite.db")
    cursor = conn.cursor()
    
    # Check if record exists
    cursor.execute("SELECT * FROM students WHERE ID = ?", (Id,))
    isRecordExist = cursor.fetchone() is not None
    
    # Insert or update based on existence
    if isRecordExist:
        cursor.execute("UPDATE students SET Name = ?, Age = ? WHERE ID = ?", (Name, Age, Id))
    else:
        cursor.execute("INSERT INTO students (ID, Name, Age) VALUES (?, ?, ?)", (Id, Name, Age))
    
    conn.commit()
    conn.close()

Id = input('Enter User Id: ')
name = input('Enter User Name: ')
age = input('Enter User Age: ')

create_table()
insertOrUpdate(Id, name, age)


sampleNum = 0
while True:
    ret, img = cam.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = faceDetect.detectMultiScale(gray, 1.3, 5)
    
    for (x, y, w, h) in faces:
        sampleNum += 1
        # Save the captured image into the datasets folder
        cv2.imwrite(f"dataset/User.{Id}.{sampleNum}.jpg", gray[y:y+h, x:x+w])
        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        # Add delay to ensure proper capture
        cv2.waitKey(400)
    
    cv2.imshow("Face", img)
    
    # Break the loop after 20 images have been taken
    if sampleNum >= 20:
        break
    
    # Add delay for displaying frames
    cv2.waitKey(1)

cam.release()
cv2.destroyAllWindows()




