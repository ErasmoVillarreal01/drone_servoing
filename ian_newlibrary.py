from djitellopy import Tello
import logging
import cv2, time
from threading import Thread
 
tello = Tello()
 
tello.connect()
 
keepRecording = True
tello.streamon()
frame_read = tello.get_frame_read()
 
def videoRecorder():
    # create a VideoWrite object, recoring to ./video.avi
    # 创建一个VideoWrite对象，存储画面至./video.avi
    height, width, _ = frame_read.frame.shape
    video = cv2.VideoWriter('video.avi', cv2.VideoWriter_fourcc(*'XVID'),  20, (960,720))
    
 
    while keepRecording:
        # video.write(frame_read.frame)
        cv2.imshow('drone',frame_read.frame)
        time.sleep(1 / 30)
 
    video.release()
 
recorder = Thread(target=videoRecorder)
recorder.start()
 
tello.takeoff()
time.sleep(2)
tello.land()
 
keepRecording = False
recorder.join()
 
cv2.destroyAllWindows()
 
 
 
# Tello.LOGGER.setLevel(logging.DEBUG)
 
# print(tello.get_battery())
 
 
# tello.takeoff()
 
# tello.move_left(30)
# tello.move_forward(30)
 
# tello.land()
# tello = Tello()
# tello.connect()