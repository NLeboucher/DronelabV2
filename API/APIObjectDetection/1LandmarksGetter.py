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

# Create a RealSense align object for aligning color and depth frames
align = rs.align(rs.stream.color)

cv2.namedWindow('Intel RealSense Webcam Feed', cv2.WINDOW_NORMAL)

# Initiate holistic model
with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
    while True:
        # Wait for a coherent pair of frames: depth and color
        frames = pipeline.wait_for_frames()
        aligned_frames = align.process(frames)
        color_frame = aligned_frames.get_color_frame()
        depth_frame = aligned_frames.get_depth_frame()

        if not color_frame or not depth_frame:
            continue

        # Get intrinsics for depth frame
        depth_intrin = depth_frame.profile.as_video_stream_profile().intrinsics

        # Convert the RealSense frame to an OpenCV image
        frame = np.asanyarray(color_frame.get_data())

        # Recolor Feed
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False

        # Make Detections
        results = holistic.process(image)

        # Recolor image back to BGR for rendering
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Process each type of landmarks
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
                        cv2.putText(image, f"{landmark_type} {landmark_id}: ({x:.2f}, {y:.2f}, {z:.2f})", 
                                    (pixel_x, pixel_y), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 0), 1, cv2.LINE_AA)

        # Draw MediaPipe landmarks
        mp_drawing.draw_landmarks(image, results.face_landmarks, mp_holistic.FACEMESH_CONTOURS)
        mp_drawing.draw_landmarks(image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
        mp_drawing.draw_landmarks(image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)

        cv2.imshow('Intel RealSense Webcam Feed', image)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

# Stop and release the RealSense pipeline
pipeline.stop()
cv2.destroyAllWindows()