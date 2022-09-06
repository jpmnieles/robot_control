"""Script for Grace Robot Saccade Movement and Display
"""

import os
import sys
sys.path.append(os.path.join(os.path.realpath(__file__), '..\..'))

import time
import datetime
import cv2 as cv

from grace.system import Grace
from grace.capture import LeftEyeCapture, RightEyeCapture


# Initialization
grace = Grace(degrees=True)
left_cam = LeftEyeCapture()
right_cam = RightEyeCapture()

# Instruction
print("Press the following keys for specific actions: \
\n  m: move eye motors\
\n  l: save left eye cam image\
\n  r: save right eye cam image\
\n  s: save both left and right eye cam image\
\n  esc: save right eye cam image" )
input("Press Enter to continue...")

# Program
while(1):
    try:
        cv.imshow("Left Camera", left_cam.frame)
    except:
        pass
    
    try:
        cv.imshow("Right Camera", right_cam.frame)
    except:
        pass

    key = cv.waitKey(1)

    if key == 109:  # letter m
        """Control the eye motors. Press '\m' key
        """
        temp = input("---------------\nInput pan and tilt values (l_eye_pan, r_eye_pan, tilt): ")
        angles = eval(temp)
        grace.move_both_eyes(angles)
    elif key == 108:  # letter l
        """Save left eye camera image. Press 'l' key
        """
        frame = left_cam.frame
        print("Left Eye Camera Shape:", frame.shape)
        date_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f") 
        fn_str = 'results/' + date_str + '_left_eye.png'
        cv.imwrite(fn_str, frame)
        print("Saving Left Camera Image to: ", fn_str)
    elif key == 114:  # letter r
        """Save right eye camera image. Press 'r' key
        """
        frame = right_cam.frame
        print("Right Eye Camera:", frame.shape)
        date_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f") 
        fn_str = 'results/' + date_str + '_right_eye.png'
        cv.imwrite(fn_str, frame)
        print("Saving Left Camera Image to: ", fn_str)
    elif key == 115:  # letter s
        """Save both left & right eye camera image. Press 'r' key
        """
        l_frame = left_cam.frame
        r_frame = right_cam.frame
        print("Left Eye Camera Shape:", l_frame.shape)
        print("Right Eye Camera:", r_frame.shape)
        date_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f") 
        l_fn_str = 'results/' + date_str + '_left_eye.png'
        r_fn_str = 'results/' + date_str + '_right_eye.png'
        cv.imwrite(l_fn_str, l_frame)
        cv.imwrite(r_fn_str, r_frame)
        print("Saving Left Camera Image to: ", l_fn_str)
        print("Saving Right Camera Image to: ", r_fn_str)
    elif key == 27:  # Esc
        """Execute end of program. Press 'esc' key to escape program
        """
        del left_cam
        del right_cam
        break
