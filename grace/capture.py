"""Module for Capturing Camera Frames from Grace Robot
"""


import cv2 as cv
import datetime


class BaseCapture(object):
    

    def __init__(self) -> None:
        self._frame = None


    @property
    def frame(self):
        raise(NotImplementedError)



class LeftEyeCapture(BaseCapture):


    INDEX = 0  # Index is variable based on USB Connection


    def __init__(self, index=None) -> None:
        super().__init__()
        if index == None:
            index = self.INDEX
        self.cap = cv.VideoCapture(index)


    @property
    def frame(self):
        ret, frame = self.cap.read()
        if not ret:
            print('Left Eye Camera: No Captured Frame')        
        return frame


    def __exit__(self):
        self.cap.release()


class RightEyeCapture(BaseCapture):


    INDEX = 2  # Index is variable based on USB Connection


    def __init__(self, index=None) -> None:
        super().__init__()
        if index == None:
            index = self.INDEX
        self.cap = cv.VideoCapture(index)


    @property
    def frame(self):
        ret, frame = self.cap.read()
        if not ret:
            print('Right Eye Camera: No Captured Frame')        
        return frame


    def __exit__(self):
        self.cap.release()


if __name__ == "__main__":
    
    left_cam = LeftEyeCapture()
    right_cam = RightEyeCapture()

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

        if key == 108:  # letter l
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
