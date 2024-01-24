import cv2 as cv2
import numpy as np
import pyrealsense2 as rs
 
 
dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
parameters =  cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(dictionary, parameters)

fps = 30
 
def aruco_display(corners, ids, rejected, image):
    if len(corners) > 0:
 
        ids = ids.flatten()
 
        for (markerCorner, markerID) in zip(corners, ids):
            corners = np.squeeze(markerCorner)
            (topLeft, topRight, bottomRight, bottomLeft) = corners
 
            topRight = (int(topRight[0]), int(topRight[1]))
            bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
            bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
            topLeft = (int(topLeft[0]), int(topLeft[1]))
 
            cv2.line(image, topLeft, topRight, (255, 0, 0), 2)
            cv2.line(image, topRight, bottomRight, (0, 255, 0), 2)
            cv2.line(image, bottomRight, bottomLeft, (0, 0, 255), 2)
            cv2.line(image, bottomLeft, topLeft, (0, 255, 0), 2)
 
            cX = int((topLeft[0] + bottomRight[0]) / 2.0)
            cY = int((topLeft[1] + bottomRight[1]) / 2.0)
            cv2.circle(image, (cX, cY), 4, (0, 0, 255), -1)
 
            cv2.putText(image, str(markerID), (topLeft[0], topLeft[1] - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (0, 255, 0), 2)
            print("[Inference] ArUco marker ID: {}".format(markerID))
 
    return image


if __name__ == '__main__':
    import sys
    sys.path.append("..")
    from utilities.Camera import *
    # # Configure depth and color streams
    # pipeline = rs.pipeline()
    # config = rs.config()

    # # Get device product line for setting a supporting resolution
    # pipeline_wrapper = rs.pipeline_wrapper(pipeline)
    # pipeline_profile = config.resolve(pipeline_wrapper)
    # device = pipeline_profile.get_device()
    # device_product_line = str(device.get_info(rs.camera_info.product_line))

    # found_rgb = False
    # for s in device.sensors:
    #     if s.get_info(rs.camera_info.name) == 'RGB Camera':
    #         s.set_option(rs.option.exposure, 100)  # Set your desired exposure value here
    #         found_rgb = True
    #         break
    # if not found_rgb:
    #     print("The demo requires Depth camera with Color sensor")
    #     exit(0)

    # config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, fps)
    # config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, fps)

    # # Start streaming
    # pipeline.start(config)
    
    # cap = cv2.VideoCapture(0)

    cam = rsCamera()
    cv2.namedWindow("Markers", cv2.WINDOW_NORMAL) 
    cv2.resizeWindow("Markers", 800, 600)   

    
    while True:
    
        # frames = pipeline.wait_for_frames()
        # color_frame = frames.get_color_frame()
        # color_image = np.asanyarray(color_frame.get_data())

        color_image,_ = cam.getNextFrame()
    
        markerCorners, markerIds, rejectedCandidates = detector.detectMarkers(color_image)
    
        print(markerCorners)
    
        detected_markers = aruco_display(markerCorners, markerIds, rejectedCandidates, color_image)
    
        cv2.imshow("Markers", detected_markers)
    
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q") or cv2.getWindowProperty("Markers",cv2.WND_PROP_VISIBLE) < 1:
            break
    
    cv2.destroyAllWindows()
    cam.stop()
    # cap.release()