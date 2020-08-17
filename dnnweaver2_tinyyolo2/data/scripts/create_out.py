#!/local/workspace/tools/anaconda3/envs/tfpy36cpuenv/bin/python
import sys
import os
import array
import numpy as np
import collections
import cv2 as cv2
from darkflow.net.build import TFNet

np.set_printoptions(threshold=sys.maxsize)
np.set_printoptions(precision=10)
np.set_printoptions(suppress=True)
np.set_printoptions(linewidth=np.inf)

def unpad_tensor(fpga_pad, shape, data):
    print ("unpad_tensor: t.fpga_pad: {}, t.shape: {}".format(fpga_pad, shape))
    return data[
            fpga_pad[0][0]:fpga_pad[0][0]+shape[0],
            fpga_pad[1][0]:fpga_pad[1][0]+shape[1],
            fpga_pad[2][0]:fpga_pad[2][0]+shape[2],
            fpga_pad[3][0]:fpga_pad[3][0]+shape[3]
            ] 

def fxp16tofp32_tensor(tensor, num_frac_bits):
    print ("num_frac_bits: {}".format(num_frac_bits))
    pow_nfb_tensor = np.full(tensor.shape, np.float32(pow(2, num_frac_bits)), dtype=np.float32)
    shifted_tensor = np.float32(tensor) / pow_nfb_tensor
    return shifted_tensor

    
def get_bbox(tfnet, box_input, h, w):
    boxes = tfnet.framework.findboxes(box_input)

    #print ("boxes:\n{}".format(boxes))
    threshold = tfnet.FLAGS.threshold
    print ("threshold: {}".format(threshold))
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

#a = np.ones([1,13,13,128], dtype = np.int16)
##print (a)
#
#fd = os.open("converted.bin", os.O_CREAT|os.O_RDWR)
#os.write(fd, a)
#os.close(fd)

fd = os.open("converted.bin", os.O_RDWR)
got_out_fpga = np.array(array.array('h', os.read(fd, 1*13*13*128*2)), dtype=np.int16).reshape((1,13,13,128))
os.close(fd)
print ("got_out_fpga.shape {}".format(got_out_fpga.shape))
got_out_fpga = unpad_tensor(((0, 0), (0, 0), (0, 0), (0, 3)), (1, 13, 13, 125), got_out_fpga)
print ("new got_out_fpga.shape {}".format(got_out_fpga.shape))

got_out_fpga = fxp16tofp32_tensor(got_out_fpga, 11)

print (got_out_fpga)
out_tensors_d = collections.OrderedDict()
out_tensors_d["conv8"] = [got_out_fpga, 12, 100]
print ("=============================")
print (out_tensors_d["conv8"][0][0])

h = 600
w = 960

threshold = 0.25

options = {"model": "conf/tiny-yolo-voc.cfg", "load": "conf/tiny-yolo-voc.weights", "threshold": 0.25}
tfnet = TFNet(options)

result = get_bbox(tfnet, out_tensors_d["conv8"][0][0], h, w)
input_png = "../sample/test.jpg"
input_im = cv2.imread(input_png, cv2.IMREAD_COLOR)
font = cv2.FONT_HERSHEY_SIMPLEX
for det in result:
    label, l, r, t, b = det['label'], det['topleft']['x'], det['bottomright']['x'], det['topleft']['y'], det['bottomright']['y']
    cv2.rectangle(input_im, (l, b), (r, t), (0, 255, 0), 2)
    #if "4.0.0" in cv2.__version__:
    cv2.putText(input_im, label, (l, b), font, 1, (255, 255, 255), 2, cv2.LINE_AA)
    #elif "2.4.9.1" in cv2.__version__:
    #    cv2.putText(input_im, label, (l, b), font, 1, (255, 255, 255), 2, cv2.CV_AA)
    #else:
    #    raise Exception("Unknown cv2 version")

cv2.imwrite(os.path.join(os.path.dirname(input_png), "bbox-" + os.path.basename(input_png)), input_im)
