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
import pickle
import pandas as pd
import numpy as np
import cv2 as cv

from grace.capture import LeftEyeCapture, RightEyeCapture
from grace.control import MultiMotorCtrl
from grace.system import Grace


class BaselineImageCapture(object):
    

    DEVICES = ['left_eye', 'right_eye']
    _pan_position = None
    _tilt_position = None
    _images = None


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
        # self.eyelid_ctrl = MultiMotorCtrl(self.grace.ros.ros_client,
        #                                   ['UpperLidLeft', 'UpperLidRight', 'LowerLidLeft', 'LowerLidRight'],
        #                                   degrees=True)
        # self.eyelid_ctrl.move([18, -18, -44, 44])

        self.criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        self.data = {
            "trials": None,
            "delta": None,
            "min_pan": None,
            "max_pan": None,
            "min_tilt": None,
            "max_tilt": None,
            "horz_sweep": None,
            "vert_sweep": None,
            "pan_position": None,
            "tilt_position": None,
            "origin_points": None,
            "origin_images": None,
            "origin_pan_position": None,
            "origin_tilt_position": None,
            "chessboard_points": None,
            "images": None,
        }


    def _get_init(self, trials, horz_num, vert_num):
        data = [None]*trials
        for i in range(trials):
            data[i] = [None]*vert_num
        for trial in range(trials):
            for vert in range(vert_num):
                data[trial][vert] = [None]*horz_num
        return data

    
    def _init_data(self):
        self.data["pan_position"] = self._get_init(self.trials, len(self.horz_sweep), len(self.vert_sweep))
        self.data["tilt_position"] = self._get_init(self.trials, len(self.horz_sweep), len(self.vert_sweep))
        self.data["origin_points"] = self._get_init(self.trials, len(self.horz_sweep), len(self.vert_sweep))
        self.data["origin_images"] = self._get_init(self.trials, len(self.horz_sweep), len(self.vert_sweep))
        self.data["origin_pan_position"] = self._get_init(self.trials, len(self.horz_sweep), len(self.vert_sweep))
        self.data["origin_tilt_position"] = self._get_init(self.trials, len(self.horz_sweep), len(self.vert_sweep))
        self.data["chessboard_points"] = self._get_init(self.trials, len(self.horz_sweep), len(self.vert_sweep))
        self.data["images"] = self._get_init(self.trials, len(self.horz_sweep), len(self.vert_sweep))


    def set_delta(self, delta):
        self.delta = delta
        self.data["delta"] = self.delta


    def set_limits(self, min_pan, max_pan, min_tilt, max_tilt):
        # Storing Variables
        self.min_pan = min_pan
        self.max_pan = max_pan
        self.min_tilt = min_tilt
        self.max_tilt = max_tilt
        self.data["min_pan"] = self.min_pan
        self.data["max_pan"] = self.max_pan
        self.data["min_tilt"] = self.min_tilt
        self.data["max_tilt"] = self.max_tilt

        # Sweeping Initialization
        self.horz_sweep = sorted(list(range(0, min_pan-1, -self.delta)) + list(range(self.delta, max_pan+1, self.delta)))
        self.vert_sweep = sorted(list(range(0, min_tilt-1, -self.delta)) + list(range(self.delta, max_tilt+1, self.delta)))
        self.data["horz_sweep"] = self.horz_sweep
        self.data["vert_sweep"] = self.vert_sweep

        # Grid Array Initialization
        self.pixel_x = np.zeros((len(self.vert_sweep), len(self.horz_sweep)))
        self.pixel_y = np.zeros((len(self.vert_sweep), len(self.horz_sweep)))
        self.position_pan = np.zeros((len(self.vert_sweep), len(self.horz_sweep)))
        self.position_tilt = np.zeros((len(self.vert_sweep), len(self.horz_sweep)))


    def set_trials(self, trials):
        self.trials = trials
        self.data["trials"] = self.trials
   

    def get_chessboard_points(self, img):
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        ret, corners = cv.findChessboardCorners(gray, (9,6),None)
        if ret == True:
            r_corners = cv.cornerSubPix(gray, corners, (11,11), (-1,-1), self.criteria)
            s_corners = r_corners.squeeze()
        return s_corners


    def sweep_positions(self):
        self._init_data()
        for trial in range(self.trials):
            for row,vert in enumerate(self.vert_sweep):
                for col,horz in enumerate(self.horz_sweep):
                    print("===Trial: %d, Vert: %d, Horz: %d===" % (trial, vert, horz))

                    # Origin
                    self.grace.reset_eyes()
                    time.sleep(0.2)
                    org_img = self.cam.frame
                    if self.device == 'left_eye':
                        temp = self.grace.state
                        org_state = (temp[0], temp[2])
                    elif self.device == 'right_eye':
                        temp = self.grace.state
                        org_state = (temp[1], temp[2])
                    self.data["origin_pan_position"][trial][row][col] = org_state[0]
                    self.data["origin_tilt_position"][trial][row][col] = org_state[1]
                    self.data["origin_points"][trial][row][col] = self.get_chessboard_points(org_img)
                    self.data["origin_images"][trial][row][col] = org_img
                    # cv.imshow('Img', org_img)  # Debug
                    # cv.waitKey(500)  # Debug

                    # Specific Point
                    if self.device == 'left_eye':
                        state = self.grace.move_left_eye((horz, vert))
                    elif self.device == 'right_eye':
                        state = self.grace.move_right_eye((horz, vert))
                    time.sleep(0.2)
                    img = self.cam.frame
                    self.data["pan_position"][trial][row][col] = state[0]
                    self.data["tilt_position"][trial][row][col] = state[1]
                    self.data["chessboard_points"][trial][row][col] = self.get_chessboard_points(img)
                    self.data["images"][trial][row][col] = img

                    # cv.imshow('Img', img)  # Debug
                    # cv.waitKey(500)  # Debug

    
    def save_data(self):
        # Making Directory
        filename = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f") + "_" + self.device + "_delta" + str(self.delta)
        filepath = os.path.join(os.path.abspath(""), "results", filename)
        
        # Saving to Pickle File
        with open(filepath + ".pickle", 'wb') as file:
            pickle.dump(self.data, file)
        print('Data save in:', filepath)


if __name__ == "__main__":
    # Instantiation
    start = time.time()
    baseline_capture = BaselineImageCapture(device='left_eye')

    # Initialization
    baseline_capture.set_trials(10)
    baseline_capture.set_delta(8)
    baseline_capture.set_limits(min_pan=-8, max_pan=8, min_tilt=-8, max_tilt=8)

    # Sweeping Parameters
    baseline_capture.sweep_positions()
    baseline_capture.save_data()

    # Time Elapsed
    end = time.time()
    print("Elapsed Time (sec):", end-start)
