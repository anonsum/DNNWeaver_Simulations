import av
import numpy as np
import cv2 as cv2
from time import time, sleep

from util.thread import thread_print

def video_control(drone, frame_q, frame_l, bbox_q, bbox_l, capture_q, capture_l, kill_q, done_q):
    
    thread_print ("Video Control Thread Starts")   
    video_stream = drone.get_video_stream()
    container = av.open(video_stream)

    bbox = []
    frame_count = 0
    font = cv2.FONT_HERSHEY_SIMPLEX
    frame_skip = 600
    
    out_break = False
    prev_time = 0.0
    y2t_fps_str = "YOLO2-TINY FPS: 0.0"
    while True:
        for frame in container.decode(video=0):
            start = time()
            if 0 < frame_skip:
                frame_skip -= 1
                continue
            frame_count = frame_count + 1
            if frame_count % 3 == 0 or frame_count % 3 == 1: # Dropping 33% of frames
                im = np.array(frame.to_image()) # im.shape = (row=720, column=960, rgb=3)

                cur_frame = cv2.cvtColor(im, cv2.COLOR_RGB2BGR)

                with frame_l:
                    if frame_q.empty():
                        frame_q.put(cur_frame)

                with bbox_l:
                    if not bbox_q.empty():
                        bbox, fps = bbox_q.get()
                        y2t_fps_str = "YOLO2-TINT FPS: %.1f" % fps

                for tup in bbox:
                    label, l, r, t, b = tup
                    cv2.rectangle(cur_frame, (l, b), (r, t), (0, 255, 0), 2)
                    cv2.putText(cur_frame, label, (l, b), font, 1, (255, 255, 255), 2, cv2.CV_AA)
                end = time()
#                drone_fps_str = "WEBCAM FPS: %.1f" % (1.0 / (end - start))
#                cv2.putText(cur_frame, drone_fps_str, (50, 50), font, 1, (51, 255, 255), 2, cv2.CV_AA)
#                cv2.putText(cur_frame, y2t_fps_str, (50, 100), font, 1, (51, 255, 255), 2, cv2.CV_AA)

                with capture_l:
                    if not capture_q.empty():
                        capture_q.get()
                        cv2.imwrite('capture-' + str(time()) + '.png', cur_frame)
                cv2.imshow('Drone Demo', cur_frame)
                cv2.waitKey(1)
