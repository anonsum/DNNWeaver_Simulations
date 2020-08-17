import signal
import os
import sys
import copy
import numpy as np
from time import sleep
from multiprocessing import Process, Queue, Lock, Pipe
from tensorflow.python.client import device_lib

from util.thread import thread_print
from key import GetKey
from drone import drone_control
from webcam import webcam_control
from videofile import videofile_control
from detection import detection

def drain_queue(queues):
    for q in queues:
        if not q.empty():
           q.get()

def run(cam_source, yolo_engine, tf_weight_pickle, dnnweaver2_weight_pickle, in_videofile, out_videofile):

    # Synchronous queues
    frame_q = Queue(maxsize=1)
    bbox_q = Queue(maxsize=1)
    kill_q = Queue(maxsize=1)
    key_q = Queue(maxsize=1)
    num_processes = 2
    done_q = Queue(maxsize=num_processes) 

    # Multiprocessing locks
    frame_l = Lock()
    bbox_l = Lock()
    key_l = Lock()

    # Drone management process
    if cam_source == "drone": 
        droneProcess = Process(target=drone_control, args=(frame_q, frame_l, bbox_q, bbox_l, key_q, key_l, kill_q, done_q, ))
        droneProcess.start()
    elif cam_source == "webcam": 
        webcamProcess = Process(target=webcam_control, args=(frame_q, frame_l, bbox_q, bbox_l, kill_q, done_q, )) 
        webcamProcess.start()
    elif cam_source == "videofile":
        videofileProcess = Process(target=videofile_control, args=(frame_q, frame_l, bbox_q, bbox_l, kill_q, done_q, in_videofile, out_videofile, )) 
        videofileProcess.start()

    # Object detection process using YOLO algorithm
    if yolo_engine == "tf-cpu":
        proc = "cpu"
    elif yolo_engine == "tf-gpu":
        proc = "gpu"
    elif yolo_engine == "dnnweaver2":
        proc = "gpu"
    detectionProcess = Process(target=detection, args=(yolo_engine, tf_weight_pickle, dnnweaver2_weight_pickle, frame_q, frame_l, bbox_q, bbox_l, kill_q, done_q, proc, ))
#    detectionProcess = Process(target=detection, args=(yolo_engine, tf_weight_pickle, dnnweaver2_weight_pickle, frame_q, frame_l, bbox_q, bbox_l, kill_q, done_q, proc, True, ))
    detectionProcess.start()

    # Keyboard input handler
    inkey = GetKey()
    thread_print ("Keyboard Input Handler Starts")
    while True: 
        try:
            key = inkey()
            key = ord(key)
            with key_l:
                if key_q.empty():
                    key_q.put(key)
            if key == 101: # key = 'e' 
                break
        except KeyboardInterrupt:
            break
    thread_print ("Keyboard Input Handler Ends")

    # Notifying all processes/threads to die
    kill_q.put(True)
    print ("Sent KILL Signal")

    # Wait the processes to end 
    while done_q.qsize() != num_processes:
        sleep(0.5)

    # Flush all entires in queueus
    drain_queue([frame_q, bbox_q, kill_q, key_q])
    if cam_source == "drone":
        droneProcess.join()
    elif cam_source == "webcam":
        webcamProcess.join()
    detectionProcess.join()

def main():
    if len(sys.argv) < 5:
        print ("Usage: ./drone.py <drone|webcam|videofile> <tf-cpu|tf-gpu|dnnweaver2> <tf-weight.pickle> <dnnweaver2-weight.pickle> [in_videofile] [out_videofile]")
        sys.exit()
    else:
        cam_source = sys.argv[1]
        if not (cam_source == "drone" or cam_source == "webcam" or cam_source == "videofile"):
            print ("Unknown camera source: " + str(cam_source))
            raise
        yolo_engine = sys.argv[2]
        if not (yolo_engine == "tf-cpu" or yolo_engine == "tf-gpu" or yolo_engine == "dnnweaver2"):
            print ("Unknown YOLO engine: " + str(yolo_engine))
            raise
        tf_weight_pickle = sys.argv[3]
        dnnweaver2_weight_pickle = sys.argv[4]
        if cam_source == "videofile":
            in_videofile = sys.argv[5]
            out_videofile = sys.argv[6]
        else:
            in_videofile = None
            out_videofile = None

    print ("Yolo2 Object Detection Program Starts")
    run(cam_source, yolo_engine, tf_weight_pickle, dnnweaver2_weight_pickle, in_videofile, out_videofile)
    print ("Yolo2 Object Detection Program Ends")

if __name__ == '__main__':
    main()
