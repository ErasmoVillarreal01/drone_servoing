import time 
from robomaster import robot
import cv2 as cv2
from threading import Thread

tl_drone = robot.Drone()
tl_drone.initialize()
tl_flight = tl_drone.flight

keepRecording = True
epsilon = 10

area = 0
area_threshold = 3000

diff_x = 0

#CHECAR BIEN LA ORIENTACION Y LOS VALORES DE DIF_POS
def follow_anomaly(dif_pos):
    a, b, c, d = 0,0,0,0
    
    if dif_pos > epsilon:
        d = 20
        print("GIRA DERECHA", dif_pos)
        return a,b,c,d
    elif dif_pos < -epsilon:
        d = -20
        print("GIRA IZQUIERDA", dif_pos)
        return a,b,c,d
    else:
        d = 0
        print("ESTA DENTRO DEL RANGO LA ANOMALIA", dif_pos)
        return a,b,c,d

def choose_trajec():
    global area, area_threshold, diff_x
    i=0
    dt=0.1
    while(i<20/dt):
        print("area={}".format(area))
        drone_a, drone_b, drone_c, drone_d = None,None,None,None
        if(area > area_threshold): #Anomaly Detected
            print("stopped")
            #drone_a=0; drone_b=0; drone_c=0; drone_d=0
            drone_a, drone_b, drone_c, drone_d = follow_anomaly(diff_x)
        else: # Default Trajectory
            print("regular trajectory")
            drone_a=20; drone_b=20; drone_c=0; drone_d=40
        print("a={},b={},c={},d={}".format(drone_a,drone_b,drone_c,drone_d))
        tl_flight.rc(a=drone_a,b=drone_b,c=drone_c,d=drone_d)
        time.sleep(dt)
        i+=1
    print("SE DETIENE")
    tl_flight.rc(a=0,b=0,c=0,d=0)
    time.sleep(1)
   

        


def recordVideo():
    global area, area_threshold
    print("Joining Camera")
    tl_camera = tl_drone.camera
    tl_camera.start_video_stream(display=False)
    tl_camera.set_fps('high')
    tl_camera.set_resolution("high")
    tl_camera.set_bitrate(6)
    writer_anomalies= cv2.VideoWriter('anomalies.mp4', cv2.VideoWriter_fourcc(*'DIVX'), 20, (960,720))
    writer= cv2.VideoWriter('fullTrayectory.mp4', cv2.VideoWriter_fourcc(*'DIVX'), 20, (960,720))

    while keepRecording:
        global diff_x
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
            if area > area_threshold:
                #print("ANOMALIA, grabando...")
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

               # follow_anomaly(diff_x)


                nuevoContorno = cv2.convexHull(c)
                # rospy.loginfo("{}, {}".format(cx,cy))
                cv2.putText(result, '{},{}'.format(diff_x,diff_y), (cx+10,cy),cv2.FONT_HERSHEY_SIMPLEX, 0.75,(0,255,0),1,cv2.LINE_AA) # diff x y diff y
                cv2.putText(result, msg, (center_x+10,center_y+10),cv2.FONT_HERSHEY_SIMPLEX, 0.75,(0,255,0),1,cv2.LINE_AA) # en q cuadrante esta o si esta en el centro
                cv2.putText(result, "{}".format(area), (center_x+40,center_y+40),cv2.FONT_HERSHEY_SIMPLEX, 0.75,(255,255,255),1,cv2.LINE_AA) # area
                # cv2.putText(result, '{}'.format(), (cx+10,cy-10),cv2.FONT_HERSHEY_SIMPLEX, 0.75,(0,255,0),1,cv2.LINE_AA)
                cv2.circle(result,(cx,cy),7, (0,255,0), -1) # circulo centro
                cv2.drawContours(result, [nuevoContorno], -1, (255,0,0), 3)
                #print('Diff from center: {},{}'.format(diff_x,diff_y))
                writer_anomalies.write(result)
        cv2.imshow("dron", result)
        writer.write(result)

        cv2.waitKey(1)
        
    writer.release()
    writer_anomalies.release()
    tl_camera.stop_video_stream()



if __name__ == '__main__':


    thread = Thread(target=recordVideo)
    thread.start()

    # Set the QUAV to takeoff
    tl_flight.takeoff().wait_for_completed()

    choose_trajec()
    # Add a delay to remain in hover   
    # Set the QUAV to land
    tl_flight.land().wait_for_completed()

    keepRecording = False
    thread.join()
    # Close resources
    tl_drone.close()

    
    cv2.destroyAllWindows()