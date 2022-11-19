"""Utilities for Grace Robot
"""


import os
import sys
sys.path.append(os.path.join(os.path.realpath(__file__), '..\..'))

import numpy as np
import roslibpy
import yaml


def generate_triangle_wave(init_amp, min_amp, max_amp, step_size, num_cycles, include_init):
    """Generates a triangular wave with positive and negative peaks

    Args:
        init_amp (float): initial amplitude
        min_amp (float): minimum amplitude peak
        max_amp (float): maximum amplitude peak
        step_size (float): amplitude resolution
        num_cycles (int): number of cycles of the triangular wave
        include_init (bool_): will or will not include initial amplitude in the end of waveform

    Returns:
        numpy array:
    """
    int_init_amp = round(init_amp/step_size)
    int_max_amp = round(max_amp/step_size)
    int_min_amp = round(min_amp/step_size)
    int_sweep = list(range(int_init_amp, int_max_amp+1)) + list(range(int_max_amp-1, int_min_amp-1, -1)) + list(range(int_min_amp+1, int_init_amp))
    single_sweep = [step_size*x for x in int_sweep]

    triangle_wave = []
    for _ in range(num_cycles):
        triangle_wave += single_sweep
    if include_init:
        triangle_wave.append(int_init_amp*step_size)
    return np.array(triangle_wave)


def generate_target_wave(target_amp, init_amp, step_size, num_cycles):
    int_target_amp = round(target_amp/step_size)
    int_init_amp = round(init_amp/step_size)
    int_sweep = [int_init_amp]*2 + list(range(int_init_amp, int_target_amp+1))
    addtl_sweep = list(range(int_target_amp-1, int_init_amp-1, -1)) + list(range(int_init_amp+1, int_target_amp+1))

    triangle_wave = int_sweep
    if num_cycles>1:
        for _ in range(num_cycles-1):
            triangle_wave += addtl_sweep
    target_wave = [step_size*x for x in triangle_wave]
    return np.array(target_wave)


def rmse(predictions, targets):
    return np.sqrt(((predictions - targets) ** 2).mean())


class ROSClient(object):
    

    def __init__(self, ip="BodyNC-NUC", port=9090):
        self.ROS_IP = ip
        self.ROS_PORT = port

        self.client = roslibpy.Ros(host=self.ROS_IP, port=self.ROS_PORT)
        self.client.run()
        self.ping()


    @property
    def ros_client(self):
        return self.client


    def ping(self):
        if self.client.is_connected:
            print('[ROS Client] ROS Connection Successful at http://%s:%d' % (self.ROS_IP, self.ROS_PORT))


    def __exit__(self):
        self.client.terminate()


class BaseMotorCtrl(object):
    

    def __init__(self, client) -> None:
        self.client = client
        self.talker = roslibpy.Topic(self.client, 
                                     name='/hr/actuators/pose',
                                     message_type='hr_msgs/TargetPosture')
        self.listener = roslibpy.Topic(self.client,
                                       name='/hr/actuators/motor_states',
                                       message_type='hr_msgs/MotorStateList')


    def move(self):
        raise(NotImplementedError)


    @property
    def state(self):
        raise(NotImplementedError)
    
    def __exit__(self):
        self.talker.unadvertise()
        self.listener.unsubscribe()


# Loading Motors Yaml File
with open(os.path.join(os.path.realpath(__file__), '../..', 'config/head/motors.yaml'), "r") as stream:
    try:
        head_dict = yaml.safe_load(stream)
    except yaml.YAMLError as error:
        print(error)

with open(os.path.join(os.path.realpath(__file__), '../..', 'config/body/motors.yaml'), "r") as stream:
    try:
        body_dict = yaml.safe_load(stream)
    except yaml.YAMLError as error:
        print(error)

motors_dict = {}
motors_dict.update(head_dict['motors'])
motors_dict.update(body_dict['motors'])
