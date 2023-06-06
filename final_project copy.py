import robomaster
import time 
from robomaster import robot
import cv2 as cv2

tl_drone = robot.Drone()
tl_drone.initialize()
tl_flight = tl_drone.flight


tl_camera = tl_drone.camera

tl_camera.start_video_stream(display=False)
tl_camera.set_fps('high')
tl_camera.set_resolution("high")
tl_camera.set_bitrate(6)

keepRecording = True



def tracking():
    for i in range(0,1500):
        img = tl_camera.read_cv2_image()
        hsv_frame = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
        orange_mask = cv2.inRange(hsv_frame, (105,118,102), (179, 255  , 255))
        contours,_  = cv2.findContours(orange_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        result = img.copy()
        diff_x, diff_y = 0, 0
        height, width,_ = result.shape
        # rospy.loginfo("{}x{}".format(height, width))
        center_x, center_y = int(width/2), int(height/2)
        cv2.circle(result,(center_x,center_y),7, (255,0,0), -1)
        ## TODO: Hacer este procedimiento solo con el que tenga el area mas grande
        for c in contours:
            area = cv2.contourArea(c)
            if area > 400:
                M = cv2.moments(c)
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
 
                diff_x, diff_y = cx-center_x, center_y-cy
 
                # rospy.loginfo("{}, {}".format(diff, cy-center_y))
                msg = ""
                epsilon = 50
                if(abs(diff_x)<epsilon and abs(diff_y)<epsilon):
                    msg="center"
                elif(diff_x>0 and diff_y>0):
                    msg="1"
                elif(diff_x<0 and diff_y>0):
                    msg="2"
                elif(diff_x<0 and diff_y<0):
                    msg="3"
                elif(diff_x>0 and diff_y<0):
                    msg="4"
 
 
                nuevoContorno = cv2.convexHull(c)
                # rospy.loginfo("{}, {}".format(cx,cy))
                cv2.putText(result, '{},{}'.format(diff_x,diff_y), (cx+10,cy),cv2.FONT_HERSHEY_SIMPLEX, 0.75,(0,255,0),1,cv2.LINE_AA) # diff x y diff y
                cv2.putText(result, msg, (center_x+10,center_y+10),cv2.FONT_HERSHEY_SIMPLEX, 0.75,(0,255,0),1,cv2.LINE_AA) # en q cuadrante esta o si esta en el centro
                cv2.putText(result, "{}".format(area), (center_x+40,center_y+40),cv2.FONT_HERSHEY_SIMPLEX, 0.75,(255,255,255),1,cv2.LINE_AA) # area
                # cv2.putText(result, '{}'.format(), (cx+10,cy-10),cv2.FONT_HERSHEY_SIMPLEX, 0.75,(0,255,0),1,cv2.LINE_AA)
                cv2.circle(result,(cx,cy),7, (0,255,0), -1) # circulo centro
                cv2.drawContours(result, [nuevoContorno], -1, (255,0,0), 3)
        cv2.imshow("Drone",result)
        cv2.waitKey(1)
    cv2.destroyAllWindows()
    tl_camera.stop_video_stream()

def choose_trajec(path):
    if (path == "square"):
        print("Initiating movement SQUARE")
        tl_flight.rc(a=0,b=0,c=0,d=0)
        time.sleep(20)
        tracking()
    elif(path == "circle"):
        print("Initiating movement CIRCLE")
        tl_flight.rc(a=0,b=0,c=0,d=0)
        time.sleep(20)
        tracking()
        
    else: 
        print("not valid")
        
    return

if __name__ == '__main__':

    trajec = input("What trajectory is going to be done?")

    
    # Set the QUAV to takeoff
    tl_flight.takeoff().wait_for_completed()
    time.sleep(2)

    while(True):
        choose_trajec(trajec)
        break
    # Add a delay to remain in hover
    
    print("Remaning in hover")
    time.sleep(5)
    # Set the QUAV to land
    tl_flight.land().wait_for_completed()

    # Close resources
    tl_drone.close()