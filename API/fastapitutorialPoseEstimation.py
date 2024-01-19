from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import asyncio
import cv2
import mediapipe as mp
import numpy as np
import pyrealsense2 as rs
import threading
import queue

app = FastAPI()
port = 8002
results_queue = queue.Queue()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Pose Estimation</title>
    </head>
    <body>
        <h1>Pose Estimation Coordinates</h1>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:""" + str(port) + """/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                console.log(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
        </script>
    </body>
</html>
"""

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def sendCoordinates(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

    async def broadcast_landmarks(self):
        while True:
            if not results_queue.empty():
                landmarks_data = results_queue.get()
                for landmark_id, x, y, z in landmarks_data:
                    message = f"{landmark_id},{x},{y},{z}"
                    await self.sendCoordinates(message)
            await asyncio.sleep(0.01)  # Adjust sleep time as needed

manager = ConnectionManager()

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await asyncio.sleep(50)  # Keep the connection alive
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.on_event("startup")
async def start_broadcasting():
    asyncio.create_task(manager.broadcast_landmarks())

def pose_estimation_thread():
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    pipeline.start(config)
    align = rs.align(rs.stream.color)

    mp_holistic = mp.solutions.holistic
    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        try:
            while True:
                frames = pipeline.wait_for_frames()
                aligned_frames = align.process(frames)
                color_frame = aligned_frames.get_color_frame()
                depth_frame = aligned_frames.get_depth_frame()

                if not color_frame or not depth_frame:
                    continue

                depth_intrin = depth_frame.profile.as_video_stream_profile().intrinsics
                frame = np.asanyarray(color_frame.get_data())
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image.flags.writeable = False

                results = holistic.process(image)

                landmarks_data = []
                for landmarks in [results.pose_landmarks]:
                    if landmarks:
                        for landmark_id, landmark in enumerate(landmarks.landmark):
                            pixel_x = int(landmark.x * color_frame.width)
                            pixel_y = int(landmark.y * color_frame.height)
                            if 0 <= pixel_x < depth_frame.width and 0 <= pixel_y < depth_frame.height:
                                depth = depth_frame.get_distance(pixel_x, pixel_y)
                                point = rs.rs2_deproject_pixel_to_point(depth_intrin, [pixel_x, pixel_y], depth)
                                x, y, z = point
                                landmarks_data.append((landmark_id, x, y, z))
                results_queue.put(landmarks_data)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        finally:
            pipeline.stop()

threading.Thread(target=pose_estimation_thread, daemon=True).start()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
