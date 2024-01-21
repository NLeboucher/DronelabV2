from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

import asyncio
import cv2
import mediapipe as mp
import numpy as np
import pyrealsense2 as rs
import os, sys
import uvicorn
path = os.getcwd()
folders = path.split("/")
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
logger = Logger("logH.txt",True)

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

@app.get("/HelloWorld/")
async def read_root():
    return {"message": "Welcome to the human pose API"}


@app.get("/")
async def get():
    return FileResponse('API/static/index.html')

@app.get("/calibrate")
async def calibrate():
    config = rs.config()
    pipeline = rs.pipeline()
    pipeline.start(config)

    # Get stream profile and camera intrinsics
    profile = pipeline.get_active_profile()
    depth_profile = rs.video_stream_profile(profile.get_stream(rs.stream.depth))
    depth_intrinsics = depth_profile.get_intrinsics()
    w, h = depth_intrinsics.width, depth_intrinsics.height
    # Get camera intrinsics from the profile
    intr = profile.get_stream(rs.stream.color).as_video_stream_profile().get_intrinsics()
    camera_matrix = np.array([[intr.fx, 0, intr.ppx],
                            [0, intr.fy, intr.ppy],
                            [0, 0, 1]])
    dist_coeffs = np.array(intr.coeffs)

    nw = 4
    nh = 3
    square_size = 0.0505  # Size of a chessboard square in meters

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    #description des points du chessboard
    objp = np.zeros((nw*nh,3), np.float32)
    objp[:,:2] = np.mgrid[0:nw,0:nh].T.reshape(-1,2)
    objp *= square_size

    rot_mat = None
    tvecs = None
    frames = pipeline.wait_for_frames()

    color_frame = frames.get_color_frame()

    color_image = np.asanyarray(color_frame.get_data())

    rot_mat, tvecs = to_word_coord(color_image,nw,nh,criteria,objp,camera_matrix,dist_coeffs)
    print(rot_mat)
    print(tvecs)
    return tvecs

def to_word_coord(img,nw,nh,criteria,objp,camera_matrix,dist_coeffs):
    global rot_mat
    global tvecs
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    ret, corners = cv2.findChessboardCorners(gray, (nw,nh),None,flags=cv2.CALIB_CB_FAST_CHECK)
    if ret == True:
        corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
        # Find the rotation and translation vectors.
        ret,rvecs, tvecs = cv2.solvePnP(objp, corners2, camera_matrix, dist_coeffs)

        rot_mat,_ = cv2.Rodrigues(rvecs)

    

    # if tvecs is not None:
    #     # apply the rotation and translation vectors to the vertices
    #     return np.matmul(verts - np.transpose(tvecs), rot_mat)
    return  rot_mat, tvecs
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
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
        await manager.disconnect(websocket)
        print("Websocket closed")

def main(host="0.0.0.0", port=8001):

    uvicorn.run("mainO:app", host=host, port=port)
