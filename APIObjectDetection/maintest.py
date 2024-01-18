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

# Initiate holistic model
with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
    while True:
        # Wait for a frame from the RealSense camera
        frames = pipeline.wait_for_frames()
        aligned_frames = align.process(frames)
        color_frame = aligned_frames.get_color_frame()
        depth_frame = aligned_frames.get_depth_frame()
        
        if not color_frame or not depth_frame:
            continue

        # Convert the RealSense frame to an OpenCV image
        frame = np.asanyarray(color_frame.get_data())

        # Recolor Feed
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        depth_intrin = depth_frame.profile.as_video_stream_profile().intrinsics
        # Make Detections
        results = holistic.process(image)

        # Recolor image back to BGR for rendering
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # 1. Draw face landmarks and display coordinates in 3D space
        if results.face_landmarks:
            for idx, landmark in enumerate(results.face_landmarks.landmark):
                if not landmark.HasField('visibility'):
                    continue
                if landmark.visibility > 0.5:
                    # Convert 2D pixel coordinates to 3D world coordinates
                    pixel_x = int(landmark.x * color_frame.width)
                    pixel_y = int(landmark.y * color_frame.height)
                    depth_value = depth_frame.get_distance(pixel_x, pixel_y)
                    print(depth_value)
                    point = rs.rs2_deproject_pixel_to_point(depth_intrin, [pixel_x, pixel_y], depth_value)
                    x, y, z = point
                    print(x, y, z)
                    cv2.putText(image, f"Landmark {idx}: ({x:.2f}, {y:.2f}, {z:.2f})", (pixel_x, pixel_y),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 255), 1, cv2.LINE_AA)

        # Repeat similar code for right_hand_landmarks, left_hand_landmarks, and pose_landmarks
        # ...

        cv2.imshow('Intel RealSense Webcam Feed', image)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

# Stop and release the RealSense pipeline
pipeline.stop()
cv2.destroyAllWindows()