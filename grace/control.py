"""Module for Controlling the Motors of Grace Robot
"""


import time
from math import radians
import roslibpy

from .utils import ROSClient, BaseMotorCtrl


class MultiMotorCtrl(BaseMotorCtrl):


    def __init__(self, client, actuator_list, degrees=True) -> None:
        super().__init__(client)
        self.actuator_list = actuator_list
        self.quantity = len(self.actuator_list)
        self.degrees = degrees
        self._state_list = [{'target': None, 'position': None, 'load': None, 'timestamp': None} for _ in range(self.quantity)]
    

    def move(self, position):
        for i in range(self.quantity):
            self._state_list[i]['target'] = position[i]
            if self.degrees:
                position[i] = radians(position[i])
        self.talker.publish(roslibpy.Message({'names': self.actuator_list,
                                              'values': position}))
        time.sleep(0.2)


    def _capture_state(self, msg):
        for actuator in msg['motor_states']:
            for i in range(self.quantity):
                if actuator['name'] == self.actuator_list[i]:
                    self._state_list[i]['position'] = actuator['position']
                    self._state_list[i]['load'] = actuator['load']
                    self._state_list[i]['timestamp'] = actuator['timestamp']


    @property
    def state(self):
        self.listener.subscribe(self._capture_state)
        time.sleep(0.2)
        self.listener.unsubscribe()
        return self._state_list
    
    @property
    def motors(self):
        return self.actuator_list


if __name__ == "__main__":
    # Initialization
    grace = ROSClient()
    
    # Left and Right Eye Control
    lr_pan = MultiMotorCtrl(grace.ros_client, ['EyeTurnLeft', 'EyeTurnRight'])
    lr_pan.move([-10, 10])
    print(lr_pan.state)
    
    # Right Arm Control
    r_arm = MultiMotorCtrl(grace.ros_client, ['RightShoulderPitch'])
    r_arm.move([-10])
    print(r_arm.state)
