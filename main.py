import cv2
import face_recognition
import os
import time
import numpy as np
import asyncio
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Create directories if they don't exist
if not os.path.exists('unknown_faces'):
    os.makedirs('unknown_faces')

if not os.path.exists('detected_faces'):
    os.makedirs('detected_faces')

def get_current_ids_count(directory_path):
    try:
      # Get the list of all entries in the directory
      entries = os.listdir(directory_path)
      
      # Filter out only the directories
      folders = [entry for entry in entries if os.path.isdir(os.path.join(directory_path, entry))]
      
      # Return the count of folders
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
current_id = get_current_ids_count('unknown_faces')
face_id_counter = 0
new_face_detected = False
face_timestamps = defaultdict(lambda: time.time() - 61)  # Stores the last time the face was seen
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

def save_face(face_encoding, frame, top, right, bottom, left):
    global current_id, face_id_counter
    
    # Generate a unique ID for the face
    face_id = f"person_{current_id}"
    current_id += 1
    
    padding = 100  # Increase this value to capture a larger area
    top = max(0, top - padding)
    right = min(frame.shape[1], right + padding)
    bottom = min(frame.shape[0], bottom + padding)
    left = max(0, left - padding)
    
    # Create a folder for the new face
    face_folder = os.path.join('unknown_faces', face_id)
    os.makedirs(face_folder, exist_ok=True)
    
    # Save the face image
    face_image = frame[top:bottom, left:right]
    image_path = os.path.join(face_folder, f"{face_id_counter}.jpg")
    cv2.imwrite(image_path, face_image)
    face_id_counter += 1
    
    # Add the face encoding to known faces
    known_face_encodings.append(face_encoding)
    known_face_ids.append(face_id)
    
    print(f"New face detected and saved with ID: {face_id}")
    return face_id

async def detect_and_label_faces(frame):
    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Find all the faces and face encodings in the current frame of video
    face_locations = await asyncio.get_event_loop().run_in_executor(executor, face_recognition.face_locations, rgb_frame)
    face_encodings = await asyncio.get_event_loop().run_in_executor(executor, face_recognition.face_encodings, rgb_frame, face_locations)
    
    face_labels = []
    
    for face_encoding, (top, right, bottom, left) in zip(face_encodings, face_locations):
        if known_face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            
            best_match_index = np.argmin(face_distances)
            print("Match index:", best_match_index)
            print("matches[best_match_index]", matches[best_match_index])
            print("face_distances[best_match_index]", face_distances[best_match_index])
            if matches[best_match_index] and face_distances[best_match_index] < 0.5:
                # If a match was found in known_face_encodings, use the known face ID
                face_id = known_face_ids[best_match_index]
                face_timestamps[face_id] = time.time()
            else:
                # If no match was found, save the new face
                if time.time() - face_timestamps["new_face"] > 10:
                    face_id = await asyncio.get_event_loop().run_in_executor(executor, save_face, face_encoding, frame, top, right, bottom, left)
                    face_timestamps["new_face"] = time.time()
                else:
                    face_id = "Unknown"
                    
        else:
            # No known faces, save the new face
            face_id = await asyncio.get_event_loop().run_in_executor(executor, save_face, face_encoding, frame, top, right, bottom, left)
            face_timestamps["new_face"] = time.time()
        
        face_labels.append(face_id)
        
        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, face_id, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
    
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

from pydantic import BaseModel
class StreamRequest(BaseModel):
    inputType: str
    inputValue: str
    
@app.post('/start_stream')
async def start_stream(request: StreamRequest):
  try:
      input_type = request.inputType
      input_value = request.inputValue
      
      if input_type not in ["camera", "rtsp"]:
          raise HTTPException(status_code=400, detail="Invalid input type")

      stream_url = f"http://localhost:8000/video_feed?input_type={input_type}&input_value={input_value}"
      return {"streamUrl": stream_url}
  except Exception as e:
      raise HTTPException(status_code=500, detail=str(e))

@app.get('/video_feed')
async def video_feed(request: Request):
    input_type = request.query_params.get('input_type')
    input_value = request.query_params.get('input_value')
    
    if input_type == 'camera':
        return StreamingResponse(generate_frames(camera_index=input_value), media_type='multipart/x-mixed-replace; boundary=frame')
    elif input_type == 'rtsp':
        return StreamingResponse(generate_frames(rtsp_url=input_value), media_type='multipart/x-mixed-replace; boundary=frame')
    else:
        raise HTTPException(status_code=400, detail="Invalid input type")