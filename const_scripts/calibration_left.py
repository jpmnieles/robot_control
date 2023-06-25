"""Example Script for Camera Calibration"""

import os
import sys
sys.path.append(os.path.join(os.path.realpath(__file__), '..\..'))

import datetime
import numpy as np
import cv2 as cv
import glob  # In Python, the glob module is used to retrieve files/pathnames matching a specified pattern


### Finding of Corner Features ###

SQUARE_LENGTH = 47  # mm

# Algorithm termination criteria (max number of iterations and/or desired accuracy)
# criteria = (count, max_iter, epsilonm)
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)  # cv.TERM_CRITERIA_EPS=2, cv.TERM_CRITERIA_MAX_ITER=1, 

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((6*9,3), np.float32)  # (num of intersection pts, 3 coord "x,y,z")
objp[:,:2] = np.mgrid[0:9,0:6].T.reshape(-1,2) * SQUARE_LENGTH  # mgrid is meshgrid, # reshape(-1, 2) means numpy will figure out based on number

# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.
images = glob.glob(os.path.join(os.path.realpath(__file__), '..\..', 'results/230529_left/*.png'))

for fname in images:
    img = cv.imread(fname)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    # Find the chess board corners
    ret, corners = cv.findChessboardCorners(gray, (9,6), None)  # (mat, pattern_size, output_array)

    # If found, add object points, image points (after refining them)
    if ret == True:
        objpoints.append(objp)

        corners2 = cv.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)
        imgpoints.append(corners)

        # Draw and display the corners
        cv.drawChessboardCorners(img, (9,6), corners2, ret)  # size=(pts per row, pts per column)
        cv.imshow('img', img)
        cv.waitKey(100)

cv.destroyAllWindows()


### Calibration ###

ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
print(mtx)
print(dist)
np.savez(os.path.join(os.path.abspath(""), "results","230529_left", "camera_mtx.npz"), mtx=mtx, dist=dist, rvecs=rvecs, tvecs=tvecs)  # Saving parameters

### Undistortion ###
# mtx = np.array([[401.529047760177, 0, 318.1145980696263], [0, 400.2252977083747, 243.9799353278892], [ 0, 0, 1]])
# dist = np.array([[-0.02022860533660855, -0.05452208477950831, 0.003195222738222771, -0.001958983512216205, 0]])

# Refine the camera matrix based on a free scaling parameter
img = cv.imread(os.path.join(os.path.abspath(""), "results","230529_left", "20230529_223225_672392_left_eye.png"))
h,  w = img.shape[:2]
newcameramtx, roi = cv.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))  # Epsilon=1

# File Timestamp
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")

## Undistort Vanilla
# Undistort
orig_dst = cv.undistort(img, mtx, dist, None, newcameramtx)
cv.imshow('Undistorted', orig_dst)
cv.waitKey(0)
filepath = os.path.join(os.path.abspath(""), "results",  timestamp + "_calibresult0.png")
cv.imwrite(filepath, orig_dst)

# Crop the image
x, y, w, h = roi
dst = orig_dst[y:y+h, x:x+w]

filepath = os.path.join(os.path.abspath(""), "results", timestamp + "_calibresult1.png")
cv.imwrite(filepath, dst)

## Undistort Remap
# Undistort
mapx, mapy = cv.initUndistortRectifyMap(mtx, dist, None, newcameramtx, (w,h), 5)
dst = cv.remap(img, mapx, mapy, cv.INTER_LINEAR)

# Crop the image
x, y, w, h = roi
dst = orig_dst[y:y+h, x:x+w]
filepath = os.path.join(os.path.abspath(""), "results", timestamp + "_calibresult2.png")
cv.imwrite(filepath, dst)


### Re-projection Error ###
mean_error = 0
for i in range(len(objpoints)):
    imgpoints2, _ = cv.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
    error = cv.norm(imgpoints[i], imgpoints2, cv.NORM_L2)/len(imgpoints2)  # sqrt(sum(x-y)^2)/(3 coords)
    mean_error += error
print( "total error: {}".format(mean_error/len(objpoints)) )


