import asyncio
connected_clients = set()
import json

async def websocket_handler(websocket, path):
    connected_clients.add(websocket)
    print(f"New WebSocket connection established.{websocket}")
    try:
        await websocket.send(json.dumps({"message": "Connected to the server"}))
        async for message in websocket:
            print(f"Received from client: {message}")
    finally:

        connected_clients.remove(websocket)
        print("WebSocket connection closed.")

async def broadcast_message(message):
    await asyncio.gather(*(client.send(message) for client in connected_clients))

async def broadcast_face_detection(face_id, timestamp):
    message = json.dumps({
        "type": "face_detection",
        "face_id": face_id,
        "timestamp": timestamp
    })
    await broadcast_message(message)