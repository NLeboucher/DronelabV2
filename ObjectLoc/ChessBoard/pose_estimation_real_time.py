import numpy as np
import cv2 as cv
import glob
import os
# Load previously saved data
with np.load('B.npz') as X:
    mtx, dist, _, _ = [X[i] for i in ('mtx','dist','rvecs','tvecs')]

def draw(img, corners, imgpts):
    corner = corners[0].ravel().astype(int)
    img = cv.line(img, corner, imgpts[0].ravel().astype(int), (255,0,0), 5)
    img = cv.line(img, corner, imgpts[1].ravel().astype(int), (0,255,0), 5)
    img = cv.line(img, corner, imgpts[2].ravel().astype(int), (0,0,255), 5)
    return img


nw = 9
nh = 6

criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
objp = np.zeros((nw*nh,3), np.float32)
objp[:,:2] = np.mgrid[0:nw,0:nh].T.reshape(-1,2)
axis = np.float32([[3,0,0], [0,3,0], [0,0,-3]]).reshape(-1,3)

cv.namedWindow("img", cv.WINDOW_NORMAL) 
cv.resizeWindow("img", 800, 600)   

cap = cv.VideoCapture(0)

while True:
    ret, img = cap.read()
    gray = cv.cvtColor(img,cv.COLOR_BGR2GRAY)
    ret, corners = cv.findChessboardCorners(gray, (nw,nh),None,flags=(cv.CALIB_CB_FAST_CHECK))
    if ret == True:
        corners2 = cv.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
        # Find the rotation and translation vectors.
        ret,rvecs, tvecs = cv.solvePnP(objp, corners2, mtx, dist)
        # project 3D points to image plane
        imgpts, jac = cv.projectPoints(axis, rvecs, tvecs, mtx, dist)
        img = draw(img,corners2,imgpts)
    cv.imshow('img',img)
    k = cv.waitKey(1) & 0xFF
    if k == ord('q') or cv.getWindowProperty("img",cv.WND_PROP_VISIBLE) < 1:
        break
    if k == ord('s'):
        cv.imwrite('img.png', img)
cv.destroyAllWindows()