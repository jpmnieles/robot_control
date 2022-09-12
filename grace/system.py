"""Module for Controlling Grace Robot
"""


from .control import MultiMotorCtrl
from .utils import ROSClient


class Grace(object):


    def __init__(self, degrees=True) -> None:
        self.ros = ROSClient()
        self.l_eye_pan = MultiMotorCtrl(self.ros.ros_client, ['EyeTurnLeft'], degrees)
        self.r_eye_pan = MultiMotorCtrl(self.ros.ros_client, ['EyeTurnRight'], degrees)
        self.lr_eyes_tilt = MultiMotorCtrl(self.ros.ros_client, ['EyesUpDown'], degrees)
        self.lr_eyes_pan = MultiMotorCtrl(self.ros.ros_client, ['EyeTurnLeft', 'EyeTurnRight'], degrees)
        self.l_eye_pan_tilt = MultiMotorCtrl(self.ros.ros_client, ['EyeTurnLeft', 'EyesUpDown'], degrees)
        self.r_eye_pan_tilt = MultiMotorCtrl(self.ros.ros_client, ['EyeTurnRight', 'EyesUpDown'], degrees)
        self.lr_eyes_pan_tilt = MultiMotorCtrl(self.ros.ros_client, ['EyeTurnLeft', 'EyeTurnRight', 'EyesUpDown'], degrees)
        self.reset_eyes()
    

    def move_left_eye(self, angles: tuple):
        """Moves the left eye motor with pan and/or tilt values.
        
        Pan only: angles = (pan, None)
        Tilt only: angles = (None, tilt)
        Pan and Tilt: angles = (pan, tilt)
        
        Angles (tuple): (pan, tilt)
        """
        if angles[0] is None:
            self.lr_eyes_tilt.move([angles[1]])
        elif angles[1] is None:
            self.l_eye_pan.move([angles[0]])
        else:
            self.l_eye_pan_tilt.move(list(angles))
        angles = self.state
        return (angles[0], angles[2])
            
    def move_right_eye(self, angles: tuple):
        """Moves the right eye motor with pan and/or tilt values.

        Pan only: angles = (pan, None)
        Tilt only: angles = (None, tilt)
        Pan and Tilt: angles = (pan, tilt)
        
        Angles (tuple): (pan, tilt)
        """
        if angles[0] is None:
            self.lr_eyes_tilt.move([angles[1]])
        elif angles[1] is None:
            self.r_eye_pan.move([angles[0]])
        else:
            self.r_eye_pan_tilt.move(list(angles))
        angles = self.state
        return (angles[1], angles[2])

    def move_both_eyes(self, angles: tuple):
        """Moves both the left and right eye motors with pan and/or tilt values.

        Left Right Pan and Tilt: angles = (l_eye_pan, r_eye_pan, tilt)
        Left Right Pan only: angles = (l_eye_pan, r_eye_pan, None)        

        Angles (tuple): (l_eye_pan, r_eye_pan, tilt)
        """
        if angles[0] is None:
            self.move_right_eye((angles[1],angles[2]))
        elif angles[1] is None:
            self.move_left_eye((angles[0],angles[2]))
        elif angles[2] is None:
            self.lr_eyes_pan.move([angles[0],angles[1]])
        else:
            self.lr_eyes_pan_tilt.move(list(angles))
        angles = self.state
        return angles

    def reset_eyes(self):
        angles = self.move_both_eyes((0, 0, 0))
        return angles
    
    @property
    def state(self):
        temp = self.lr_eyes_pan_tilt.state
        angles = (temp[0]['actual'], temp[1]['actual'], temp[2]['actual'])
        if None in angles:
            while(not None in angles):
                temp = self.lr_eyes_pan_tilt.state
                angles = (temp[0]['actual'], temp[1]['actual'], temp[2]['actual'])
                print('Repeat')
        self._state = angles
        return self._state


if __name__ == "__main__":
    # Initialization
    grace = Grace(degrees=True)

    # Left Eye Control
    state = grace.move_left_eye((-19, -19))
    print(state)

    # Right Eye Control
    state = grace.move_right_eye((-19, None))
    print(state)

    # Both Eyes Control
    state = grace.reset_eyes()
    print(state)
