#!/usr/bin/python
import pandas as pd
import os
import sys
import numpy as np
import cv2

np.set_printoptions(threshold=sys.maxsize)
np.set_printoptions(precision=3)
np.set_printoptions(suppress=True)
np.set_printoptions(linewidth=np.inf)

def resize_input(im):
        h = 416
        w = 416
        imsz = cv2.resize(im, (w, h)) 
        imsz = imsz / 255.
        imsz = imsz[:,:,::-1]
        return imsz

def fp32tofxp16_tensor(tensor, num_frac_bits):
    pow_nfb_tensor = np.full(tensor.shape, pow(2, num_frac_bits), dtype=np.int32)
    shifted_tensor = tensor * pow_nfb_tensor
    casted_tensor = np.int16(shifted_tensor)
    return casted_tensor

def pad_tensor(data, pad, pad_value=0):
    return np.pad(data, pad, 'constant', constant_values=(pad_value, pad_value))    

input_png = "../../../sample/test.jpg"
input_im = cv2.imread(input_png, cv2.IMREAD_COLOR)
print ("input_im shape:{}".format(input_im.shape))
im = resize_input(input_im)
print ("im shape:{}".format(im.shape))
tin = np.expand_dims(im, 0)
print ("tin.shape:{}".format(tin.shape))
print ("tin:\n{}".format(tin))
_tin = fp32tofxp16_tensor(tin, 8)
print ("_tin:\n{}".format(_tin))
padded_data = pad_tensor(_tin,((0, 0), (1, 1), (1, 1), (0, 13)))
print ("Padded data:\n{}".format(padded_data))
fd = os.open("test_image.bin", os.O_CREAT|os.O_RDWR)
os.write(fd, padded_data)
os.close(fd)

