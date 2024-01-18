from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import asyncio
import cv2
import mediapipe as mp
import numpy as np
import pyrealsense2 as rs

app = FastAPI()

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
            var ws = new WebSocket("ws://localhost:8000/ws");
            window.onbeforeunload = function() {
            ws.onclose = function () {}; // disable onclose handler
            ws.close();
            };
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            
        </script>
    </body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
    # Configure RealSense pipeline
        pipeline = rs.pipeline()
        config = rs.config()
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

        # Start the RealSense pipeline
        pipeline.start(config)
        align = rs.align(rs.stream.color)

        # Initiate holistic model
        mp_holistic = mp.solutions.holistic
        with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
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

                for landmarks in [results.pose_landmarks]:
                    if landmarks:
                        for landmark_id, landmark in enumerate(landmarks.landmark):
                            pixel_x = int(landmark.x * color_frame.width)
                            pixel_y = int(landmark.y * color_frame.height)
                            if 0 <= pixel_x < depth_frame.width and 0 <= pixel_y < depth_frame.height:
                                depth = depth_frame.get_distance(pixel_x, pixel_y)
                                point = rs.rs2_deproject_pixel_to_point(depth_intrin, [pixel_x, pixel_y], depth)
                                x, y, z = point
                                await websocket.send_text(f"Landmark {landmark_id}: X={x}, Y={y}, Z={z}")

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        pipeline.stop()
    except Exception as e:
        print(e)
    finally:
        await websocket.close()
        print("Websocket closed")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
