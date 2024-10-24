import mediapipe as mp
import cv2
import pyrealsense2 as rs
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic

# Configure RealSense pipeline
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
# Start the RealSense pipeline
pipeline.start(config)
#INITIALIZE INTRINSICS
# Create a RealSense align object for aligning color and depth frames
align = rs.align(rs.stream.color)
global color_intrinsics, depth_intrinsics
color_intrinsics = None
depth_intrinsics = None
frames = pipeline.wait_for_frames()
aligned_frames = align.process(frames)
color_frame = aligned_frames.get_color_frame()
depth_frame = aligned_frames.get_depth_frame()
depth_intrin = depth_frame.profile.as_video_stream_profile().intrinsics
video_intrin = color_frame.profile.as_video_stream_profile().intrinsics
_intrinsics = rs.intrinsics()
print(_intrinsics, "///",depth_intrin, "///", video_intrin)
print(".modified bc",rs.distortion.modified_brown_conrady)
print(".none",rs.distortion.none)
print(".inverse_brown_conrady",rs.distortion.inverse_brown_conrady)
print(".ftheta",rs.distortion.ftheta)
print(".brown_conrady",rs.distortion.brown_conrady)
print(".kannala_brandt4",rs.distortion.kannala_brandt4)
# print(".kannala_brandt6",rs.distortion.kannala_brandt6)
# print(".last",rs.distortion.last)
# print("distortion_none",rs.distortion.distortion_none)
# print("distortion_ftheta",rs.distortion.distortion_ftheta)
# print("distortion_inverse_brown_conrady",rs.distortion.distortion_inverse_brown_conrady)
# print("distortion_modified_brown_conrady",rs.distortion.distortion_modified_brown_conrady)
# print("distortion_brown_conrady",rs.distortion.distortion_brown_conrady)
# print("distortion_kannala_brandt4",rs.distortion.distortion_kannala_brandt4)
# print("distortion_kannala_brandt6",rs.distortion.distortion_kannala_brandt6)
# print("distortion.distortion_last",rs.distortion.distortion_last)
# print("distortion.distortion_max",rs.distortion.distortion_max)
# _intrinsics.width = cameraInfo.width
# _intrinsics.height = cameraInfo.height
# _intrinsics.ppx = cameraInfo.K[2]
# _intrinsics.ppy = cameraInfo.K[5]
# _intrinsics.fx = cameraInfo.K[0]
# _intrinsics.fy = cameraInfo.K[4]
# #_intrinsics.model = cameraInfo.distortion_model
# _intrinsics.model  = pyrealsense2.distortion.none     
# _intrinsics.coeffs = [i for i in cameraInfo.D]