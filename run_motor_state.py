import time
import datetime
import json
import pickle
from turtle import left
import numpy as np
import cv2 as cv
import pandas as pd
import matplotlib.pyplot as plt

from matplotlib.animation import FuncAnimation
import psutil
import collections


from grace.system import Grace

# Initialization
grace = Grace(degrees=True)

def get_position(index):
    state = grace.lr_eyes_pan_tilt.state
    angle = state[index]['actual']
    return angle


# function to update the data
def my_function(i):
    # get data
    left_eye.popleft()
    left_eye.append(get_position(index=0))
    right_eye.popleft()
    right_eye.append(get_position(index=1))
    updown_eyes.popleft()
    updown_eyes.append(get_position(index=2))
    # clear axis
    ax.cla()
    ax1.cla()
    ax2.cla()
    ax.set_title("Left Eye Pan Position")
    ax1.set_title("Right Eye Pan Position")
    ax2.set_title("Both Eyes Tilt Position")
    # plot pan left eye
    ax.plot(left_eye)
    ax.scatter(len(left_eye)-1, left_eye[-1])
    ax.text(len(left_eye)-1, left_eye[-1]+2, "{}".format(left_eye[-1]))
    ax.set_ylim(-40,40)
    # plot pan right eye
    ax1.plot(right_eye)
    ax1.scatter(len(right_eye)-1, right_eye[-1])
    ax1.text(len(right_eye)-1, right_eye[-1]+2, "{}".format(right_eye[-1]))
    ax1.set_ylim(-40,40)
    # plot tilt
    ax2.plot(updown_eyes)
    ax2.scatter(len(updown_eyes)-1, updown_eyes[-1])
    ax2.text(len(updown_eyes)-1, updown_eyes[-1]+2, "{}".format(updown_eyes[-1]))
    ax2.set_ylim(-40,40)
# start collections with zeros
left_eye = collections.deque(np.zeros(10))
right_eye = collections.deque(np.zeros(10))
updown_eyes = collections.deque(np.zeros(10))
# define and adjust figure
fig = plt.figure(figsize=(12,6), facecolor='#DEDEDE')
ax = plt.subplot(131)
ax1 = plt.subplot(132)
ax2 = plt.subplot(133)
ax.set_facecolor('#DEDEDE')
ax1.set_facecolor('#DEDEDE')
ax2.set_facecolor('#DEDEDE')

# animate
ani = FuncAnimation(fig, my_function, interval=10)

plt.show()