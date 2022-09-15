"""Script for Capturing the Angle-Pixel Pair Baseline of Grace
"""


import os
import sys
from tabnanny import filename_only
sys.path.append(os.path.join(os.path.realpath(__file__), '..\..'))

import time
import json
import datetime
import random
import pandas as pd
import numpy as np
import cv2 as cv

from grace.capture import LeftEyeCapture, RightEyeCapture
from grace.control import MultiMotorCtrl
from grace.system import Grace


class BaselineCapture(object):
    

    DEVICES = ['left_eye', 'right_eye']


    def __init__(self, device, undistort=False) -> None:
        if device not in self.DEVICES:
            raise(Exception("Device not found"))
        self.device = device
        if self.device == 'left_eye':
            self.cam = LeftEyeCapture()
        elif self.device == 'right_eye':
            self.cam = RightEyeCapture()
        
        if undistort:
            pass

        self.grace = Grace(degrees=True)
        self.eyelid_ctrl = MultiMotorCtrl(self.grace.ros.ros_client,
                                          ['UpperLidLeft', 'UpperLidRight', 'LowerLidLeft', 'LowerLidRight'],
                                          degrees=True)
        self.eyelid_ctrl.move([18, -18, -44, 44])

        self.criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    

    def set_delta(self, delta):
        self.delta = delta


    def set_limits(self, min_pan, max_pan, min_tilt, max_tilt):
        # Storing Variables
        self.min_pan = min_pan
        self.max_pan = max_pan
        self.min_tilt = min_tilt
        self.max_tilt = max_tilt

        # Sweeping Initialization
        self.horz_sweep = sorted(list(range(0, min_pan-1, -self.delta)) + list(range(self.delta, max_pan+1, self.delta)))
        self.vert_sweep = sorted(list(range(0, min_tilt-1, -self.delta)) + list(range(self.delta, max_tilt+1, self.delta)))

        # Grid Array Initialization
        self.pixel_x = np.zeros((len(self.vert_sweep), len(self.horz_sweep)))
        self.pixel_y = np.zeros((len(self.vert_sweep), len(self.horz_sweep)))
        self.position_pan = np.zeros((len(self.vert_sweep), len(self.horz_sweep)))
        self.position_tilt = np.zeros((len(self.vert_sweep), len(self.horz_sweep)))
   

    def get_chessboard_points(self, img):
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        ret, corners = cv.findChessboardCorners(gray, (9,6),None)
        if ret == True:
            r_corners = cv.cornerSubPix(gray, corners, (11,11), (-1,-1), self.criteria)
            s_corners = r_corners.squeeze()
        return s_corners


    def capture_base_position(self, loop=10):
        base_positions= []
        for _ in range(loop):
            self.grace.reset_eyes()
            if self.device == 'left_eye':
                self.grace.move_left_eye((random.randint(self.min_pan, self.max_pan),
                                        random.randint(self.min_tilt, self.max_tilt)))
            elif self.device == 'right_eye':
                self.grace.move_right_eye((random.randint(self.min_pan, self.max_pan),
                                        random.randint(self.min_tilt, self.max_tilt)))
            self.grace.reset_eyes()
            time.sleep(0.2)
            img = self.cam.frame
            corners = self.get_chessboard_points(img)
            base_positions.append(corners)
            print("Base Corners:", corners)
            cv.imshow('Img', img)  # Debug
            cv.waitKey(500)  # Debug
        self.base_position = np.mean(base_positions, axis=0)
        return self.base_position
    

    def process_pixel_diff(self, corners):
        diff_corners = corners - self.base_position
        ave_value = np.mean(diff_corners, axis=0)
        ave_value = np.round(ave_value).astype(int)
        return ave_value
    

    def sweep_positions(self):
        self.grace.reset_eyes()
        for row,vert in enumerate(self.vert_sweep):
            for col,horz in enumerate(self.horz_sweep):
                if self.device == 'left_eye':
                    state = self.grace.move_left_eye((horz, vert))
                elif self.device == 'right_eye':
                    state = self.grace.move_right_eye((horz, vert))
                time.sleep(0.2)

                # Capture Points
                img = self.cam.frame
                corners = self.get_chessboard_points(img)
                ave_value = self.process_pixel_diff(corners)

                # Saving of Points
                print('=========%d, %d=========' % (horz, vert))  # Debug
                self.pixel_x[row, col] = ave_value[0]
                print('Pixel X:', self.pixel_x)  # Debug
                self.pixel_y[row, col] = ave_value[1]
                print('Pixel Y:', self.pixel_y)  # Debug
                self.position_pan[row, col] = state[0]
                print('Position Pan:', self.position_pan)  # Debug
                self.position_tilt[row, col] = state[1]
                print('Position Tilt:', self.position_tilt)  # Debug

                cv.imshow('Img', img)  # Debug
                cv.waitKey(500)  # Debug
                self.grace.reset_eyes()
                time.sleep(0.2)

    
    def save_data(self):
        # Pandas Dataframe
        self.df_x = pd.DataFrame(self.pixel_x, index=self.vert_sweep, columns=self.horz_sweep, dtype=int)
        self.df_y = pd.DataFrame(self.pixel_y, index=self.vert_sweep, columns=self.horz_sweep, dtype=int)
        self.df_pan = pd.DataFrame(self.position_pan, index=self.vert_sweep, columns=self.horz_sweep)
        self.df_tilt = pd.DataFrame(self.position_tilt, index=self.vert_sweep, columns=self.horz_sweep)

        # Making Directory
        filename = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f") + "_" + self.device + "_delta" + str(self.delta)
        filepath = os.path.join(os.path.abspath(""), "results", filename)
        os.makedirs(filepath)
        
        # Saving to CSV
        self.df_x.to_csv(os.path.join(filepath, "pixel_x_" + filename + ".csv"))
        self.df_y.to_csv(os.path.join(filepath, "pixel_y_" + filename + ".csv"))
        self.df_pan.to_csv(os.path.join(filepath, "position_pan_" + filename + ".csv"))
        self.df_tilt.to_csv(os.path.join(filepath, "posiiton_tilt_" + filename + ".csv"))
        print('Data save in:', filepath)


if __name__ == "__main__":
    # Instantiation
    start = time.time()
    baseline_capture = BaselineCapture(device='left_eye')

    # Initialization
    baseline_capture.set_delta(3)
    baseline_capture.set_limits(min_pan=-19, max_pan=19, min_tilt=-40, max_tilt=40)
    
    # Capturing Base Position
    base_position = baseline_capture.capture_base_position(loop=10)
    print(base_position)

    # Sweeping Parameters
    baseline_capture.sweep_positions()
    baseline_capture.save_data()

    # Time Elapsed
    end = time.time()
    print("Elapsed Time (sec):", end-start)
