import cv2 as cv2
from time import time

from util.thread import thread_print

def webcam_control(frame_q, frame_l, bbox_q, bbox_l, kill_q, done_q):
    thread_print ("Webcam Control Process Starts")

    bbox = []
    font = cv2.FONT_HERSHEY_SIMPLEX
    cam = cv2.VideoCapture(0)
    prev_time = 0.0
    y2t_fps_str = "YOLO2-TINY FPS: 0.0"
    while kill_q.empty() :
        start = time()
        _, cur_frame = cam.read()
        cur_frame = cv2.resize(cur_frame, (1024, 768)) 
        if frame_q.empty():
            frame_q.put(cur_frame)
            
        if not bbox_q.empty():
            bbox, fps = bbox_q.get()
            y2t_fps_str = "YOLO2-TINY FPS: %.1f" % fps

        for tup in bbox:
            label, l, r, t, b = tup
            cv2.rectangle(cur_frame, (l, b), (r, t), (0, 255, 0), 2)
            cv2.putText(cur_frame, label, (l, b), font, 1, (255, 255, 255), 2, cv2.CV_AA)
        end = time()
        webcam_fps_str = "WEBCAM FPS: %.1f" % (1.0 / (end - start))
        cv2.putText(cur_frame, webcam_fps_str, (50, 50), font, 1, (51, 255, 255), 2, cv2.CV_AA)
        cv2.putText(cur_frame, y2t_fps_str, (50, 100), font, 1, (51, 255, 255), 2, cv2.CV_AA)
        cv2.imshow('Webcam Demo', cur_frame)
        cv2.waitKey(1)
    cv2.destroyAllWindows()

    done_q.put(True)
    
    thread_print ("Webcam Control Process Ends")

