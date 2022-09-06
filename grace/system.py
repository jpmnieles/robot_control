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


if __name__ == "__main__":
    # Initialization
    grace = Grace(degrees=True)

    # Left Eye Control
    grace.move_left_eye((-19, None))

    # Right Eye Control
    grace.move_right_eye((-19, -19))