import threading
from time import time, sleep
from multiprocessing import Queue, Lock

import tellopy

from video import video_control
from util.thread import thread_print

def drone_control(frame_q, frame_l, bbox_q, bbox_l, key_q, key_l, kill_q, done_q):
    drone = tellopy.Tello()
    drone.connect()
    drone.wait_for_connection(5.0)
    drone.subscribe(drone.EVENT_FLIGHT_DATA, flight_data_handler)
    
    capture_q = Queue(maxsize=1)
    capture_l = Lock()

    videoThread = threading.Thread(target=video_control, args=(drone, frame_q, frame_l, bbox_q, bbox_l, capture_q, capture_l, kill_q, done_q, ))
    videoThread.daemon = True
    videoThread.start()

    thread_print ("Drone Control Process Starts")
    drone.set_loglevel(drone.LOG_DEBUG)
    
    key = None
    while True:
        with key_l:
            if not key_q.empty():
                key = key_q.get()
            else:
                key = None
        if key == 27:  # key = esc; ignore esc inserted by python
            continue
        if key == 91:  # key = arrows; ignore 91 inserted before actual arrow's ascii value
            continue
        if key == 101: # key = 'e' 
            break
        if key == 112: # key = 'p'
            with capture_l:
                capture_q.put(True)
        if key == 116: # key = t
            drone.takeoff()
        if key == 108: # key = l
            drone.land()
        if key == 122:  # key = z
            drone.left(25)
        if key == 99: # key = c
            drone.right(25)
        if key == 115: # key = s
            drone.forward(25)
        if key == 120: # key = x
            drone.backward(25)
        if key == 46: # key = .
            drone.clockwise(35)
        if key == 117: # key = u
            drone.up(25)
        if key == 100: # key = d
            drone.down(25)
        if key == 44: # key = ,
            drone.counter_clockwise(35)
        if key == 49: # key = 1
            drone.flip_forward()
        if key == 50: # key = 2
            drone.flip_back()
        if key == 51: # key = 3
            drone.flip_right()
        if key == 52: # key = 4
            drone.flip_left()
        if key == 48:
            drone.left(0)
            drone.right(0)
            drone.forward(0)
            drone.backward(0)
            drone.clockwise(0)
            drone.up(0)
            drone.down(0)
            drone.counter_clockwise(0)
        if key is not None:
            thread_print(key)
        thread_print (str(drone.left_y) + " " + str(drone.right_y) + " " + str(drone.right_x))
        key = None
        sleep(0.1)

    done_q.put(True)

    thread_print ("Drone Control Process Ends")

prev_flight_data = None

def flight_data_handler(event, sender, data, **args):
    global prev_flight_data
    drone = sender
    if event is drone.EVENT_FLIGHT_DATA:
        if prev_flight_data != str(data):
            # Disable flight_data print so that I can see the low battery warning better
            # thread_print("\r" + str(data))
            prev_flight_data = str(data)
        if data.battery_percentage < 10:
            thread_print("DRONE MUST LAND NOW")
    else:
        thread_print('event="%s" data=%s' % (event.getname(), str(data)))

