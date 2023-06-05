import robomaster
from robomaster import robot
import numpy as np
import cv2 as cv2

def nothing(x):
    pass

cv2.namedWindow('result')
 
# Starting with 100's to prevent error while masking
h,s,v = 100,100,100
 
# Creating track bar
cv2.createTrackbar('h', 'result',0,120,nothing)
cv2.createTrackbar('s', 'result',0,255,nothing)
cv2.createTrackbar('v', 'result',0,255,nothing)


if __name__ == '__main__':
    tl_drone = robot.Drone()
    tl_drone.initialize()
 
    tl_camera = tl_drone.camera
 
    tl_camera.start_video_stream(display=False)
    tl_camera.set_fps('high')
    tl_camera.set_resolution("high")
    tl_camera.set_bitrate(6)
 
    for i in range(0,900):
        img = tl_camera.read_cv2_image()
 
 
        hsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
 
    # get info from track bar and appy to result
        h = cv2.getTrackbarPos('h','result')
        s = cv2.getTrackbarPos('s','result')
        v = cv2.getTrackbarPos('v','result')
    
        # Normal masking algorithm
        lower_blue = np.array([h,s,v])
        upper_blue = np.array([180,255,255])
    
        mask = cv2.inRange(hsv,lower_blue, upper_blue)
    
        result = cv2.bitwise_and(img,img,mask = mask)
    
 
        cv2.imshow("Drone",result)
        cv2.waitKey(1)
 
    cv2.destroyAllWindows()
 
    tl_camera.stop_video_stream()
 
    tl_drone.close()