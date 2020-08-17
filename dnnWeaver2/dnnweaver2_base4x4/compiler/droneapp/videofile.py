import cv2 as cv2
from time import time, sleep

from util.thread import thread_print

def videofile_control(frame_q, frame_l, bbox_q, bbox_l, kill_q, done_q, in_videofile, out_videofile):
    thread_print ("Videofile Control Process Starts")

    width = 1024
    height = 768
   # width = 1280
   # height = 720

    bbox = []
    font = cv2.FONT_HERSHEY_SIMPLEX
    cam = cv2.VideoCapture(in_videofile)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
    #fps = cam.get(cv2.CAP_PROP_FPS)
    out = cv2.VideoWriter(out_videofile, fourcc, 20.0, (width, height))
    #out = cv2.VideoWriter(out_videofile, fourcc, fps, (width, height))
    prev_time = 0.0
    y2t_fps_str = "YOLO2-TINY FPS: 0.0"
    done_printed = False
  #  w  = cam.get(3) # float
 #   h = cam.get(4) # float
    sleep(5)
    while kill_q.empty() :
        start = time()
        retval, cur_frame = cam.read()
        if retval == False:
            if not done_printed:
                print ("Done")
                done_printed = True
            continue
        cur_frame = cv2.resize(cur_frame, (width, height)) 
        if frame_q.empty():
            frame_q.put(cur_frame)
        sleep(0.005)
            
        if not bbox_q.empty():
            bbox, fps = bbox_q.get()
            y2t_fps_str = "YOLO2-TINY FPS: %.1f" % fps

        for tup in bbox:
            label, l, r, t, b = tup
            cv2.rectangle(cur_frame, (l, b), (r, t), (0, 255, 0), 2)
            cv2.putText(cur_frame, label, (l, b), font, 1, (255, 255, 255), 2, cv2.LINE_AA)
        end = time()
        webcam_fps_str = "VIDEOFILE FPS: %.1f" % (1.0 / (end - start))
        cv2.putText(cur_frame, webcam_fps_str, (50, 50), font, 1, (51, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(cur_frame, y2t_fps_str, (50, 100), font, 1, (51, 255, 255), 2, cv2.LINE_AA)
        out.write(cur_frame)
    out.release()
    cam.release()

    done_q.put(True)
    
    thread_print ("Videofile Control Process Ends")

