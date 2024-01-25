# License: Apache 2.0. See LICENSE file in root directory.
# Copyright(c) 2015-2017 Intel Corporation. All Rights Reserved.

"""
This sample is mostly for unit testing, but there is no reason you couldn't


Usage:
launch the script and move the camera around, you should see the human pose projected on the screen it can be rotated.
Verify that the pose is correct by looking at the web camera preview.
------
Mouse: 
    Drag with left button to rotate around pivot (thick small axes), 
    with right button to translate and the wheel to zoom.

"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from websockets.exceptions import ConnectionClosedOK
from fastapi.responses import HTMLResponse, FileResponse
import asyncio
import cv2
import mediapipe as mp
import numpy as np
import pyrealsense2 as rs
import threading
from threading import Thread, Lock

import queue

app = FastAPI()
port = 8002
IP = "localhost"
results_queue = queue.Queue()

# state variables
calibrate = False
calibrate_lock = Lock()
stop = False
stop_lock = Lock()
wascalibratedonce = False

# mount static files to /static for web server
app.mount(f"/static", StaticFiles(directory="./static"), name="static")

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def sendCoordinates(self, message: str):
        for connection in list(self.active_connections):  # Use a copy of the list to avoid modification during iteration
            try:
                await connection.send_text(message)
            except ConnectionClosedOK:
                self.disconnect(connection)  # Remove the closed connection

    async def broadcast_landmarks(self):
        print("Broadcasting landmarks")

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
    return FileResponse('./static/index.html')
@app.get("/HelloWorld/")
async def read_root():
    return {"message": "Welcome to the human pose API"}

# To the state variables
@app.get("/calibrate")
async def defcalibrate():
    global calibrate
    with calibrate_lock:
        calibrate = True
@app.get("/stop")
async def defstop():
    global stop
    with stop_lock:
        stop = True


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
    print("Starting to broadcast")
    asyncio.create_task(manager.broadcast_landmarks())

def pose_estimation_thread():
    print("started pose estimation thread")
    global calibrate
    global calibrate_lock
    global wascalibratedonce
    global stop
    global stop_lock
    global rot_mat
    global tvecs
    rot_mat = np.zeros((3,3))
    tvecs = np.zeros((3,1))
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    pipeline.start(config)

    profile = pipeline.get_active_profile()
    intr = profile.get_stream(rs.stream.color).as_video_stream_profile().get_intrinsics()
    global camera_matrix
    camera_matrix = np.array([[intr.fx, 0, intr.ppx],
                          [0, intr.fy, intr.ppy],
                          [0, 0, 1]])
    global dist_coeffs
    dist_coeffs = np.array(intr.coeffs)

    align = rs.align(rs.stream.color)
    mp_holistic = mp.solutions.holistic
    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        try:
            while True:
                # print("getting frames")

                frames = pipeline.wait_for_frames()
                aligned_frames = align.process(frames)
                color_frame = aligned_frames.get_color_frame()
                depth_frame = aligned_frames.get_depth_frame()
                # print("got frames")
                if not color_frame or not depth_frame:
                    continue

                depth_intrin = depth_frame.profile.as_video_stream_profile().intrinsics
                frame = np.asanyarray(color_frame.get_data())
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image.flags.writeable = False

                results = holistic.process(image)
                # print("got results")
                
                calibrate_lock.__enter__()

                if(calibrate):
                    print("calibrating")
                    color_image = np.asanyarray(color_frame.get_data())
                    calibration(color_image)
                    calibrate = False
                    calibrate_lock.__exit__()
                    wascalibratedonce = True
                else:
                    calibrate_lock.__exit__()
                    # print("calibate lock exited")
                    landmarks_data = []
                    for landmarks in [results.pose_landmarks]:
                        if landmarks:
                            for landmark_id, landmark in enumerate(landmarks.landmark):
                                # print("landmark id: ", landmark_id)
                    
                                pixel_x = int(landmark.x * color_frame.width)
                                pixel_y = int(landmark.y * color_frame.height)
                                if 0 <= pixel_x < depth_frame.width and 0 <= pixel_y < depth_frame.height:
                                    depth = depth_frame.get_distance(pixel_x, pixel_y)
                                    point = rs.rs2_deproject_pixel_to_point(depth_intrin, [pixel_x, pixel_y], depth)
                                    # print("tvecs: ", tvecs) 
                                    # print("point avant: ", point)
                                    pa =  np.reshape(np.matmul(np.transpose(rot_mat),point - tvecs,),-1) if wascalibratedonce else point
                                    # print("point: ", pa)
                                    x,y, z =pa[0], pa[1], pa[2]
                                    landmarks_data.append((landmark_id, x, y, z))
                    results_queue.put(landmarks_data)
                    # print("landmarks data put with",)
                with stop_lock:
                    if stop:
                        print(stop)
                        break
        finally:
            print("stopping pipeline")
            pipeline.stop()
def calibration(img, nw=3, nh=4, criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)):
    print("entered")
    global rot_mat
    global tvecs
    global camera_matrix
    global dist_coeffs
    square_size = 0.071
    objp = np.zeros((nw*nh,3), np.float32)
    objp[:,:2] = np.mgrid[0:nw,0:nh].T.reshape(-1,2)
    objp *= square_size
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    ret, corners = cv2.findChessboardCorners(gray, (nw,nh),None,flags=cv2.ADAPTIVE_THRESH_GAUSSIAN_C)
    if ret == True:
        corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
        # Find the rotation and translation vectors.
        ret,rvecs, tvecs = cv2.solvePnP(objp, corners2, camera_matrix, dist_coeffs)

        rot_mat,_ = cv2.Rodrigues(rvecs)
        print("rotation matrix: ", rot_mat)
        print("translation vector: ", tvecs)


Thread(target=pose_estimation_thread, daemon=True).start()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
    print("Starting pose estimation thread")
