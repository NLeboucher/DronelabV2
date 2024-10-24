# pip imports
import asyncio
import cv2
import json
import mediapipe as mp
import numpy as np
import os
import pyrealsense2 as rs
import sys
import websockets
from fastapi import FastAPI
import threading
import uvicorn
import time
app = FastAPI()

#local imports
path = os.getcwd()
folder = path.split("/")

if("DronelabV2" in folder):
    path = "/".join(folder[:folder.index("DronelabV2")+1])
    print(path)
else:
    Exception("Executed from Wrong folder, you need to be in DronelabV2")
sys.path.insert(0, path)
from API.logger import Logger



from API.logger import Logger

# Initialize your logger
logger = Logger("pose_estimations.log")

mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic
@app.get("/")
async def read_root():

    logger.info("root")
    return {"message": "camera control API"}

@app.websocket("/ws")
async def send_pose_data(websocket, x, y, z):
    await websocket.accept()
    logger.info(f"getting pose data")
    pose_data = json.dumps({"x": x, "y": y, "z": z})
    await websocket.send(pose_data)
    logger.info(f"Sent pose data: {pose_data}")

async def main():
    logger.info("Starting pose estimation")
    # Configure RealSense pipeline
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

    # Start the RealSense pipeline
    pipeline.start(config)
    align = rs.align(rs.stream.color)

    # Initiate holistic model
    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        async with websockets.connect("ws://localhost:8000/ws") as websocket:
            while True:
                logger.info("Waiting for frames...")
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
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                for landmarks, landmark_type in [(results.right_hand_landmarks, "Right Hand"), 
                                                 (results.left_hand_landmarks, "Left Hand"), 
                                                 (results.pose_landmarks, "Pose")]:
                    if landmarks:
                        for landmark_id, landmark in enumerate(landmarks.landmark):
                            pixel_x = int(landmark.x * color_frame.width)
                            pixel_y = int(landmark.y * color_frame.height)
                            if 0 <= pixel_x < depth_frame.width and 0 <= pixel_y < depth_frame.height:
                                depth = depth_frame.get_distance(pixel_x, pixel_y)
                                point = rs.rs2_deproject_pixel_to_point(depth_intrin, [pixel_x, pixel_y], depth)
                                x, y, z = point
                                await send_pose_data(websocket, x, y, z)

                if cv2.waitKey(10) & 0xFF == ord('q'):
                    break

    pipeline.stop()

if __name__ == "__main__":
    # Function to run the FastAPI app
    def run_fastapi():
        uvicorn.run(app, host="0.0.0.0", port=8000)

    # Start FastAPI in a background thread
    fastapi_thread = threading.Thread(target=run_fastapi)
    fastapi_thread.start()
    time.sleep(5)
    # Run the main function
    asyncio.run(main())
