import cv2
import face_recognition
import os
import time
import numpy as np
import asyncio
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import websockets
import asyncio
from websocket_handler import websocket_handler, broadcast_face_detection

# Create directories if they don't exist
if not os.path.exists('unknown_faces'):
    os.makedirs('unknown_faces')

if not os.path.exists('detected_faces'):
    os.makedirs('detected_faces')

def get_current_ids_count(directory_path):
    try:
        entries = os.listdir(directory_path)
        folders = [entry for entry in entries if os.path.isdir(os.path.join(directory_path, entry))]
        return len(folders)
    except FileNotFoundError:
        print(f"The directory '{directory_path}' does not exist.")
        return 0
    except PermissionError:
        print(f"Permission denied to access '{directory_path}'.")
        return 0

# Initialize variables
known_face_encodings = []
known_face_ids = []
# current_id = get_current_ids_count('unknown_faces')
current_id = 0
face_id_counter = 0
new_face_detected = False
face_timestamps = defaultdict(lambda: time.time() - 61)  # Stores the last time the face was seen
faces_in_previous_frame = []  # List to store face IDs and their timestamps
executor = ThreadPoolExecutor()

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB setup
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client["face_recognition_db"]
faces_collection = db["faces"]

def is_image_blurry(image, threshold=100.0):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    return laplacian_var < threshold

async def save_face(face_encoding, frame, top, right, bottom, left):
    global current_id, face_id_counter
    
    face_id = f"person_{current_id}"
    
    padding = 100
    top = max(0, top - padding)
    right = min(frame.shape[1], right + padding)
    bottom = min(frame.shape[0], bottom + padding)
    left = max(0, left - padding)
    
    face_image = frame[top:bottom, left:right]
    
    if is_image_blurry(face_image):
        print(f"Face image is too blurry to save: {face_id}")
        return "Blurry"
    
    current_id += 1

    face_folder = os.path.join('unknown_faces', face_id)
    os.makedirs(face_folder, exist_ok=True)
    
    image_path = os.path.join(face_folder, f"{face_id_counter}.jpg")
    cv2.imwrite(image_path, face_image)
    face_id_counter += 1
    
    known_face_encodings.append(face_encoding)
    known_face_ids.append(face_id)
    
    face_data = {
        "face_id": face_id,
        "image_path": image_path,
        "encoding": face_encoding.tolist(),
        "timestamp": time.time()
    }
    await faces_collection.insert_one(face_data)
    
    print(f"New face detected and saved with ID: {face_id}")
    # print(face_data)
    
    # Broadcast the face detection event
    await broadcast_face_detection(face_id, face_data["timestamp"])
    
    return face_id

async def detect_and_label_faces(frame):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = await asyncio.get_event_loop().run_in_executor(executor, face_recognition.face_locations, rgb_frame)
    face_encodings = await asyncio.get_event_loop().run_in_executor(executor, face_recognition.face_encodings, rgb_frame, face_locations)
    
    face_labels = []
    detected_faces = []
    
    for face_encoding, (top, right, bottom, left) in zip(face_encodings, face_locations):
        if known_face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            
            if matches[best_match_index] and face_distances[best_match_index] < 0.5:
                face_id = known_face_ids[best_match_index]
                face_timestamps[face_id] = time.time()
            else:
                if time.time() - face_timestamps["new_face"] > 5:
                    face_id = await save_face(face_encoding, frame, top, right, bottom, left)
                    if face_id == "Blurry":
                        face_id = "Unknown"
                    face_timestamps["new_face"] = time.time()
                else:
                    face_id = "Unknown"
                    
        else:
            face_id = await save_face(face_encoding, frame, top, right, bottom, left)
            if face_id == "Blurry":
                face_id = "Unknown"
            face_timestamps["new_face"] = time.time()
        
        face_id_str = str(face_id) if face_id is not None else "Unknown"
        face_labels.append(face_id_str)
        detected_faces.append((face_id_str, time.time()))
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, face_id_str, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
    


     # Update faces_in_previous_frame with the detected faces
    faces_in_previous_frame = detected_faces
    print("Faces in previous frame:", faces_in_previous_frame)
    
    return frame

    


async def generate_frames(camera_index=None, rtsp_url=None):
    if camera_index is not None:
        video_capture = cv2.VideoCapture(int(camera_index))
    else:
        video_capture = cv2.VideoCapture(rtsp_url)
    
    while True:
        ret, frame = video_capture.read()
        
        if not ret:
            print("Error: Unable to read frame from video stream.")
            break
        
        print("Frame captured successfully.")
        
        frame = await detect_and_label_faces(frame)
        
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            print("Error: Unable to encode frame.")
            continue
        
        frame = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
    video_capture.release()

@app.get('/video_feed')
async def video_feed(input_type: str = Query(...), input_value: str = Query(...)):
    if input_type == 'camera':
        return StreamingResponse(generate_frames(camera_index=input_value), media_type='multipart/x-mixed-replace; boundary=frame')
    elif input_type == 'rtsp':
        return StreamingResponse(generate_frames(rtsp_url=input_value), media_type='multipart/x-mixed-replace; boundary=frame')
    else:
        raise HTTPException(status_code=400, detail="Invalid input type")

def serialize_face(face):
    base_server_url = "http://localhost:3000"
    return {
        "id": str(face["_id"]),
        "face_id": face["face_id"],
        "image_path": f"{base_server_url}/{face['image_path']}",
        "encoding": face["encoding"], 
        "timestamp": face["timestamp"]
    }

@app.get('/get_faces')
async def get_faces():
    try:
        faces = await faces_collection.find().to_list(length=None)
        serialized_faces = [serialize_face(face) for face in faces]
        return JSONResponse(content={"faces": serialized_faces})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Serve static files
app.mount("/unknown_faces", StaticFiles(directory="unknown_faces"), name="unknown_faces")

async def main(): 
    try:
        print("Starting WebSocket server on port 8765")
        async with websockets.serve(websocket_handler, "0.0.0.0", 8765):
            while True:
                await asyncio.sleep(0)  # Ensure the event loop continues
    except Exception as e:
        print(f"An error occurred: {str(e)}")


try:
    asyncio.run(main())  # Start the event loop and run the main function
except RuntimeError:
    loop = asyncio.get_event_loop()
    if loop.is_running():
        print("Event loop already running. Creating a new task.")
        asyncio.ensure_future(main())