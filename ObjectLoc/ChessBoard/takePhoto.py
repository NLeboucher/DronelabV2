import cv2 as cv
import os
import Camera

def take_photo():
    dir = os.path.dirname(os.path.abspath(__file__))+"/images"
    os.makedirs(dir, exist_ok=True)
    # Open the default camera
    cap = cv.VideoCapture(0)
    cv.namedWindow("Camera", cv.WINDOW_NORMAL) 
    cv.resizeWindow("Camera", 800, 600)   

    # Check if the camera is opened successfully
    if not cap.isOpened():
        print("Unable to open the camera")
        return

    # Counter for the number of photos taken
    photo_count = 0

    # Read and display the video frames until the 'q' key is pressed
    while True:
        ret, frame = cap.read()
        cv.imshow("Camera", frame)

        key = cv.waitKey(1) & 0xFF
        if key == ord("q") or cv.getWindowProperty("Camera",cv.WND_PROP_VISIBLE) < 1:
            break
        elif key == 13 or key == 32:
            # Wait for the Enter key to be pressed
            # Save the captured frame as an image
            photo_count += 1
            cv.imwrite(f"{dir}/photo{photo_count}.jpg", frame)
            print(f"Photo {photo_count} saved successfully")
        # if key != 255:
        #     print(key)

    # Release the camera and close the window
    cap.release()
    cv.destroyAllWindows()

# Call the function to start capturing photos
take_photo()
