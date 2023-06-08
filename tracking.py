from robomaster import robot


tl_drone = robot.Drone()
tl_drone.initialize()
tl_flight = tl_drone.flight
epsilon = 20

def track(pos):
    if(pos < -epsilon):
        tl_flight.rc(a=-5,b=0,c=0,d=0)  
        print("tracking left")
    elif(pos > epsilon):
        tl_flight.rc(a=5,b=0,c=0,d=0)
        print("tracking right") 
    else:
        tl_flight.rc(a=0,b=0,c=0,d=0) 
        print("static")





    


