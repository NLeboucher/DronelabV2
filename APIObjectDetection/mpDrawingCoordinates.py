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

# Start the RealSense pipeline
pipeline.start(config)

# Initiate holistic model
with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
    while True:
        # Wait for a frame from the RealSense camera
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        if not color_frame:
            continue

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

        mp_drawing.draw_landmarks(image, results.face_landmarks, mp_holistic.FACEMESH_CONTOURS,
                                  mp_drawing.DrawingSpec(color=(80, 110, 10), thickness=1, circle_radius=1),
                                  mp_drawing.DrawingSpec(color=(80, 256, 121), thickness=1, circle_radius=1)
                                  )

        # 2. Right hand
        mp_drawing.draw_landmarks(image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS,
                                  mp_drawing.DrawingSpec(color=(80, 22, 10), thickness=2, circle_radius=4),
                                  mp_drawing.DrawingSpec(color=(80, 44, 121), thickness=2, circle_radius=2)
                                  )

        # 3. Left Hand
        mp_drawing.draw_landmarks(image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS,
                                  mp_drawing.DrawingSpec(color=(121, 22, 76), thickness=2, circle_radius=4),
                                  mp_drawing.DrawingSpec(color=(121, 44, 250), thickness=2, circle_radius=2)
                                  )

        # 4. Pose Detections
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS,
                                  mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=4),
                                  mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
                                  )


        # 1. Draw face landmarks and display coordinates
        if results.face_landmarks:
            for landmark_id, landmark in enumerate(results.face_landmarks.landmark):
                height, width, _ = image.shape
                cx, cy = int(landmark.x * width), int(landmark.y * height)
                cv2.putText(image, f"{landmark_id}: ({cx}, {cy})", (cx, cy),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 255), 1, cv2.LINE_AA)
        # Repeat similar code for right_hand_landmarks, left_hand_landmarks, and pose_landmarks
        
        # 2. Right hand
        if results.right_hand_landmarks:
            for landmark_id, landmark in enumerate(results.right_hand_landmarks.landmark):
                height, width, _ = image.shape
                cx, cy = int(landmark.x * width), int(landmark.y * height)
                cv2.putText(image, f"{landmark_id}: ({cx}, {cy})", (cx, cy),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 255), 1, cv2.LINE_AA)

        # 3. Left Hand
        if results.left_hand_landmarks:
            for landmark_id, landmark in enumerate(results.left_hand_landmarks.landmark):
                height, width, _ = image.shape
                cx, cy = int(landmark.x * width), int(landmark.y * height)
                cv2.putText(image, f"{landmark_id}: ({cx}, {cy})", (cx, cy),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 255), 1, cv2.LINE_AA)

        # 4. Pose Detections
        if results.pose_landmarks:
            for landmark_id, landmark in enumerate(results.pose_landmarks.landmark):
                height, width, _ = image.shape
                cx, cy = int(landmark.x * width), int(landmark.y * height)
                cv2.putText(image, f"{landmark_id}: ({cx}, {cy})", (cx, cy),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 255), 1, cv2.LINE_AA)

        cv2.imshow('Intel RealSense Webcam Feed', image)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

# Stop and release the RealSense pipeline
pipeline.stop()
cv2.destroyAllWindows()
