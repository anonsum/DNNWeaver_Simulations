from time import time, sleep
import numpy as np
import copy
import cv2 as cv2

from darkflow.net.build import TFNet

from util.thread import thread_print

from example.yolo_tf.yolo2_tiny_tf import YOLO2_TINY_TF
from example.dnn_fpga import dnn_fpga
from example import yolo_demo

def resize_input(input_size, im):
    h, w, c = input_size
    imsz = cv2.resize(im, (w, h))
    imsz = imsz / 255.
    imsz = imsz[:,:,::-1]
    return imsz

def get_bbox(tfnet, box_input, h, w):
    boxes = tfnet.framework.findboxes(box_input)

    threshold = tfnet.FLAGS.threshold
    boxesInfo = list()
    for box in boxes:
        tmpBox = tfnet.framework.process_box(box, h, w, threshold)
        if tmpBox is None:
            continue
        boxesInfo.append({
            "label": tmpBox[4],
            "confidence": tmpBox[6],
            "topleft": {
                "x": tmpBox[0],
                "y": tmpBox[2]},
            "bottomright": {
                "x": tmpBox[1],
                "y": tmpBox[3]}
        })
    return boxesInfo


def detection(yolo_engine, tf_w_pickle, dnnweaver2_w_pickle, frame_q, frame_l, bbox_q, bbox_l, kill_q, done_q, proc="cpu", debug=False):

    options = {"model": "conf/tiny-yolo-voc.cfg", "load": "weights/tiny-yolo-voc.weights", "threshold": 0.25}
    tfnet = TFNet(options)

    if yolo_engine == "dnnweaver2":
        fpga_manager = dnn_fpga.initialize_yolo_graph(dnnweaver2_w_pickle)
        if debug:
            y2t_tf_whole = YOLO2_TINY_TF([1, 416, 416, 3], tf_w_pickle, proc) 
    elif yolo_engine == "tf-cpu" or yolo_engine == "tf-gpu":
        y2t_tf = YOLO2_TINY_TF([1, 416, 416, 3], tf_w_pickle, proc)

    cnt = 0
    h = None
    w = None

    thread_print ("Detection Process Starts")

    cur_frame = []
    while kill_q.empty():
        with frame_l:
            if not frame_q.empty():
                cur_frame = frame_q.get()

        if cur_frame != []:
            if h == None and w == None:
                h, w, _ = cur_frame.shape

            start = time()
            if yolo_engine == "tf-cpu" or yolo_engine == "tf-gpu":
                im = resize_input((416, 416, 3), cur_frame)
                im = np.expand_dims(im, 0)
                tout = y2t_tf.inference(im)
                result = get_bbox(tfnet, tout[0], h, w) 
            elif yolo_engine == "dnnweaver2":
                im = resize_input((416, 416, 3), cur_frame)
                im = np.expand_dims(im, 0)
                _im = yolo_demo.fp32tofxp16_tensor(im, 8) 
                intermediate_tout = dnn_fpga.fpga_inference(fpga_manager, _im)
                intermediate_tout = yolo_demo.fxp16tofp32_tensor(intermediate_tout, fpga_manager.get_tout_frac_bits())

                tout = intermediate_tout

                if not debug:
                    result = get_bbox(tfnet, tout[0], h, w) 
                else: 
                    _tout = copy.deepcopy(tout)
                    result = get_bbox(tfnet, _tout[0], h, w) 

                    wnodes, wtout = y2t_tf_whole._inference(im)

                    final_tout = tout
                    final_wtout = wtout[len(wtout)-1]
                    error = np.sqrt(np.mean((final_tout - final_wtout) ** 2)) / (final_wtout.max() - final_wtout.min()) * 100.0 
                    thread_print ("Final NRMSE = %.4f%%" % error)
            end = time()
            fps = 1.0 / (end - start)

            out = []
            for det in result:
                label, l, r, t, b = det['label'], det['topleft']['x'], det['bottomright']['x'], det['topleft']['y'], det['bottomright']['y']
                out.append((label, l, r, t, b))

            with bbox_l:
                if bbox_q.empty():
                    bbox_q.put([out, fps])
        cnt += 1

    done_q.put(True)

    thread_print("Detection Process Ends..")
