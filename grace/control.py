"""Module for Controlling the Motors of Grace Robot
"""


import time
from math import radians, pi
import roslibpy
import numpy as np

from .utils import ROSClient, BaseMotorCtrl, motors_dict


class MultiMotorCtrl(BaseMotorCtrl):


    def __init__(self, client, actuator_list, degrees=True) -> None:
        super().__init__(client)
        self.actuator_list = actuator_list
        self.quantity = len(self.actuator_list)
        self.degrees = degrees
        self._motor_limits = {actuator: self._capture_limits(actuator) for actuator in actuator_list}
        self._state_list = [{'target': None, 'actual':None, 'goal': None, 'position': None, 'load': None, 'timestamp': None} for _ in range(self.quantity)]
        self.state

    def _capture_limits(self, actuator):
        min = motors_dict[actuator]['motor_min']
        init = motors_dict[actuator]['init']
        max = motors_dict[actuator]['motor_max']
        limits = {'min': min, 'init': init, 'max': max}
        return limits


    def _convert_to_angle(self, actuator, position):
        if self.degrees:
            unit = 360
        else:
            unit = pi
        angle = ((position-self._motor_limits[actuator]['init'])/4096)*unit
        return angle

    
    def _convert_to_motor_int(self, actuator, angle):
        if self.degrees:
            unit = 360
        else:
            unit = pi
        angle = round((angle/unit)*4096 + self._motor_limits[actuator]['init'])
        return angle


    def _percent_error(self, actual, measured):
        error = 100 * abs((np.array(actual) - np.array(measured)) / np.array(actual))
        return error


    def move(self, position):
        for i in range(self.quantity):
            self._state_list[i]['target'] = position[i]
            self._state_list[i]['goal'] = self._convert_to_motor_int(
                self.actuator_list[i], position[i])
            if self.degrees:
                position[i] = radians(position[i])
        
        ctr = 1
        while(True):
            self.talker.publish(roslibpy.Message({'names': self.actuator_list,
                                                'values': position}))
            time.sleep(0.75)
            curr_state = self.state
            
            goals = [curr_state[i]['goal'] for i in range(self.quantity)]
            positions = [curr_state[i]['position'] for i in range(self.quantity)]
            percent_error = self._percent_error(goals, positions)
            if all(percent_error<5):
                break
            
            if ctr == 100:
                raise(Exception("Motor command timeout. Servo motors not found"))
            else:
                ctr+=1


    def direct_move(self, position):
        for i in range(self.quantity):
            self._state_list[i]['target'] = position[i]
            self._state_list[i]['goal'] = self._convert_to_motor_int(
                self.actuator_list[i], position[i])
            if self.degrees:
                position[i] = radians(position[i])
        
        self.talker.publish(roslibpy.Message({'names': self.actuator_list,
                                              'values': position}))


    def _capture_state(self, msg):
        for actuator in msg['motor_states']:
            for i in range(self.quantity):
                if actuator['name'] == self.actuator_list[i]:
                    self._state_list[i]['actual'] = self._convert_to_angle(
                        self.actuator_list[i], actuator['position'])
                    self._state_list[i]['position'] = actuator['position']
                    self._state_list[i]['load'] = actuator['load']
                    self._state_list[i]['timestamp'] = actuator['timestamp']


    @property
    def state(self):
        self.listener.subscribe(self._capture_state)     
        return self._state_list
    
    @property
    def motors(self):
        return self.actuator_list


if __name__ == "__main__":
    # Initialization
    grace = ROSClient()
    
    # Left and Right Eye Control
    lr_pan = MultiMotorCtrl(grace.ros_client, ['EyeTurnLeft', 'EyeTurnRight', 'EyesUpDown'])
    lr_pan.move([-19, -19, -19])
    print(lr_pan.state)

    # Right Arm Control
    r_arm = MultiMotorCtrl(grace.ros_client, ['RightShoulderPitch'])
    r_arm.move([-10])
    print(r_arm.state)

    # Left and Right Eye Control
    lr_pan = MultiMotorCtrl(grace.ros_client, ['EyeTurnLeft', 'EyeTurnRight', 'EyesUpDown'])
    lr_pan.move([0, 0, 0])
    print(lr_pan.state)

    # Right Arm Control
    r_arm = MultiMotorCtrl(grace.ros_client, ['RightShoulderPitch'])
    r_arm.move([0])
    print(r_arm.state)
