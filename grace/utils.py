"""Utilities for Grace Robot
"""


import os
import sys
sys.path.append(os.path.join(os.path.realpath(__file__), '..\..'))

import roslibpy
import yaml


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
