from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

import asyncio
from threading import Thread, Lock
import cv2
import mediapipe as mp
import numpy as np
import pyrealsense2 as rs
import os, sys
import uvicorn
path = os.getcwd()
folders = path.split("/")
calibrate = False
calibrate_lock = Lock()
stop = False
stop_lock = Lock()
if("DronelabV2" in folders):
    path = "/".join(folders[:folders.index("DronelabV2")+1])
    sys.path.insert(0, path)
    from swarmcontrol import SwarmControl
    from logger import Logger
    from move import Move, Velocity
    from outputdict import OutputDict
else:
    Exception("Executed from Wrong folder, you need to be in DronelabV2")

class ConnectionManager:
    def __init__(self):
        self._active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self._active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self._active_connections.remove(websocket)

    async def sendCoordinates(self, message: str, websocket: WebSocket):
        for connection in self._active_connections:
            await connection.send_text(message)
        
manager = ConnectionManager()
app = FastAPI()
logger = Logger("logAAAAAA.txt",True)

print(f"{path}/API/static")
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount(f"/static", StaticFiles(directory="API/static"), name="static")
app.mount("/staticLandmarks", StaticFiles(directory="API/static/staticLandmarks"), name="static")
@app.get("/HelloWorld/")
async def read_root():
    return {"message": "Welcome to the human pose API"}


@app.get("/")
async def get():
    return FileResponse('API/static/index.html')

@app.get("/StaticLandmark/")
async def getTest():
    logger.info("StaticLandmark entered")
    file_path = os.path.abspath("static/staticLandmarks/index.html")
    logger.info(file_path)
    return FileResponse("API/static/staticLandmarks/index.html")


@app.get("/calibrate")
async def cal():
    global calibrate
    with calibrate_lock:
        calibrate = True
@app.get("/stop")
async def stop():
    global stop
    with stop_lock:
        stop = True

pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

# Start the RealSense pipeline
pipeline.start(config)
align = rs.align(rs.stream.color)

# Initiate holistic model
mp_holistic = mp.solutions.holistic
@app.websocket("/ws")
async def websocket_handler(websocket: WebSocket):
    await manager.connect(websocket)
    try:
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
                with calibrate_lock:
                    if(calibrate):
                        color_image = np.asanyarray(color_frame.get_data())
                        calibration(color_image)
                        calibrate = False
                    else:

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

                if stop:
                    break

            pipeline.stop()
    except Exception as e:
        print(e)
    finally:
        manager.disconnect(websocket)
def calibration(img):
    global rot_mat
    global tvecs
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    ret, corners = cv2.findChessboardCorners(gray, (nw,nh),None,flags=cv2.ADAPTIVE_THRESH_GAUSSIAN_C)
    if ret == True:
        corners2 = cv.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
        # Find the rotation and translation vectors.
        ret,rvecs, tvecs = cv2.solvePnP(objp, corners2, camera_matrix, dist_coeffs)

        rot_mat,_ = cv2.Rodrigues(rvecs)
def main(host="0.0.0.0", port=8001):
    camera_thread = Thread(target=camera_pipeline_thread)
    camera_thread.start()
    uvicorn.run("mainO:app", host=host, port=port)


