import cv2 as cv
from cv2 import aruco
import os

# dictionary to specify type of the marker
marker_dict = aruco.getPredefinedDictionary(aruco.DICT_5X5_250)

# MARKER_ID = 0
MARKER_SIZE = 400  # pixels

dir = os.path.dirname(os.path.abspath(__file__))+"/markers"
os.makedirs(dir, exist_ok=True)


# generating unique IDs using for loop
for id in range(20):  # genereting 20 markers
    # using funtion to draw a marker
    marker_image = aruco.generateImageMarker(marker_dict, id, MARKER_SIZE)
    cv.imshow("img", marker_image)
    cv.imwrite(f"{dir}/marker_{id}.png", marker_image)
    # cv.waitKey(0)
    # break

board = aruco.CharucoBoard((7,5), 1., .7, marker_dict)
imboard = board.generateImage((7*150, 5*150))
# cv.imshow("img", imboard)
# cv.waitKey(0)
cv.imwrite(f"{dir}/chessboard.png", imboard)