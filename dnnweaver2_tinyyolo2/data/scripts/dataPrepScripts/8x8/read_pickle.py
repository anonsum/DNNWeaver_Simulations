#!/usr/bin/python
import pandas as pd
import os
import sys
import numpy as np

np.set_printoptions(threshold=sys.maxsize)
np.set_printoptions(precision=3)
np.set_printoptions(suppress=True)
np.set_printoptions(linewidth=np.inf)

array_m = 8
array_n = 8

info = open("usefullInfo.txt", "w")
def pad_tensor(data, pad, pad_value=0):
    return np.pad(data, pad, 'constant', constant_values=(pad_value, pad_value))

def prep_conv_data_w(oc, kh, kw, ic, array_m, weight, pad):
    assert oc % array_m == 0
    tw = weight
    tw_data = pad_tensor(tw, pad).reshape(int(oc/array_m),array_m,kh,kw,ic)
    tw_ddr = np.transpose(tw_data, (0,2,3,4,1)).copy()
    return tw_ddr

def prep_conv_data_b(data, fpga_pad):
    tbias_ddr = np.pad(data, fpga_pad, 'constant', constant_values=(0,0))
    return tbias_ddr

def calc_nval(shape, str = ""):
    print ("Shape:{}".format(shape))
    nval = 1
    for i in range(len(shape)):
        nval = nval * shape[i]
    info.write("%s%d\n" % (str, nval))    
    return nval

object = pd.read_pickle("../../yolo2_weights/yolo2_tiny_dnnweaver2_weights.pickle")
print (type (object))
for key in object:
    layer = object[key]
    #for sub_key in layer:
    #    print ('Key: {}, Sub-key: {}'.format(key, sub_key))
    print ("Key: {}".format(key))
    if "Convolution" in key:
        weight = layer['weights']
        bias = layer['bias']
    elif "BatchNorm" in key:
        mean = layer['mean']
        scale = layer['scale']
    
   
    if "conv0/Convolution" in key:
        layer = "conv0"
        tw_ddr = prep_conv_data_w(16, 3, 3, array_n, array_m, weight, ((0, 0), (0, 0), (0, 0), (0, 5)))
        tb_ddr = prep_conv_data_b(bias, ((0,0),))
    elif "conv1/Convolution" in key:
        layer = "conv1"
        tw_ddr = prep_conv_data_w(32, 3, 3, 16, array_m, weight, ((0, 0), (0, 0), (0, 0), (0, 0)))
        tb_ddr = prep_conv_data_b(bias, ((0,0),))
    elif "conv2/Convolution" in key:
        layer = "conv2"
        tw_ddr = prep_conv_data_w(64, 3, 3, 32, array_m, weight, ((0, 0), (0, 0), (0, 0), (0, 0)))
        tb_ddr = prep_conv_data_b(bias, ((0,0),))
    elif "conv3/Convolution" in key:
        layer = "conv3"
        tw_ddr = prep_conv_data_w(128, 3, 3, 64, array_m, weight, ((0, 0), (0, 0), (0, 0), (0, 0)))
        tb_ddr = prep_conv_data_b(bias, ((0,0),))
    elif "conv4/Convolution" in key:
        layer = "conv4"
        tw_ddr = prep_conv_data_w(256, 3, 3, 128, array_m, weight, ((0, 0), (0, 0), (0, 0), (0, 0)))
        tb_ddr = prep_conv_data_b(bias, ((0,0),))
    elif "conv5/Convolution" in key:
        layer = "conv5"
        tw_ddr = prep_conv_data_w(512, 3, 3, 256, array_m, weight, ((0, 0), (0, 0), (0, 0), (0, 0)))
        tb_ddr = prep_conv_data_b(bias, ((0,0),))
    elif "conv6/Convolution" in key:
        layer = "conv6"
        tw_ddr = prep_conv_data_w(1024, 3, 3, 512, array_m, weight, ((0, 0), (0, 0), (0, 0), (0, 0)))
        tb_ddr = prep_conv_data_b(bias, ((0,0),))
    elif "conv7/Convolution" in key:
        layer = "conv7"
        tw_ddr = prep_conv_data_w(1024, 3, 3, 1024, array_m, weight, ((0, 0), (0, 0), (0, 0), (0, 0)))
        tb_ddr = prep_conv_data_b(bias, ((0,0),))
    elif "conv8/Convolution" in key:
        layer = "conv8"
        tw_ddr = prep_conv_data_w(128, 1, 1, 1024, array_m, weight, ((0, 3), (0, 0), (0, 0), (0, 0)))
        tb_ddr = prep_conv_data_b(bias, ((0,0),))
    elif "conv0/batch_norm/BatchNorm" in key:
        layer = "conv0_bn"
        tm_ddr = mean
        ts_ddr = scale
    elif "conv1/batch_norm/BatchNorm" in key:
        layer = "conv1_bn"
        tm_ddr = mean
        ts_ddr = scale
    elif "conv2/batch_norm/BatchNorm" in key:
        layer = "conv2_bn"
        tm_ddr = mean
        ts_ddr = scale
    elif "conv3/batch_norm/BatchNorm" in key:
        layer = "conv3_bn"
        tm_ddr = mean
        ts_ddr = scale
    elif "conv4/batch_norm/BatchNorm" in key:
        layer = "conv4_bn"
        tm_ddr = mean
        ts_ddr = scale
    elif "conv5/batch_norm/BatchNorm" in key:
        layer = "conv5_bn"
        tm_ddr = mean
        ts_ddr = scale
    elif "conv6/batch_norm/BatchNorm" in key:
        layer = "conv6_bn"
        tm_ddr = mean
        ts_ddr = scale
    elif "conv7/batch_norm/BatchNorm" in key:
        layer = "conv7_bn"
        tm_ddr = mean
        ts_ddr = scale
    else:
        continue

    if "conv" in layer and "_bn" not in layer: 
        st = layer + ":" + "Number of weights:"
        nval = calc_nval(tw_ddr.shape, st)
        st = layer + ":" + "Number of bias:"
        nval = calc_nval(tb_ddr.shape, st)
        print ("Key:{}, Actually going to write weights: \n{}\n{}".format(key, tw_ddr.shape, tw_ddr))
        print ("Key:{}, Actually going to write bias: \n{}\n{}".format(key, tb_ddr.shape, tb_ddr))
        filename = layer + "_weight" + ".bin"
        fd = os.open(filename, os.O_CREAT|os.O_RDWR)
        os.write(fd, tw_ddr)
        os.close(fd)
        filename = layer + "_bias" + ".bin"
        fd = os.open(filename, os.O_CREAT|os.O_RDWR)
        os.write(fd, tb_ddr)
        os.close(fd)
    elif "_bn" in layer:    
        st = layer + ":" + "Number of mean:"
        nval = calc_nval(tm_ddr.shape, st)
        st = layer + ":" + "Number of scale:"
        nval = calc_nval(ts_ddr.shape, st)
        print ("Key:{}, Actually going to write mean: \n{}\n{}".format(key, tm_ddr.shape, tm_ddr))
        print ("Key:{}, Actually going to write scale: \n{}\n{}".format(key, ts_ddr.shape, ts_ddr))
        filename = layer + "_mean" + ".bin"
        fd = os.open(filename, os.O_CREAT|os.O_RDWR)
        os.write(fd, tm_ddr)
        os.close(fd)
        filename = layer + "_scale" + ".bin"
        fd = os.open(filename, os.O_CREAT|os.O_RDWR)
        os.write(fd, ts_ddr)
        os.close(fd)
    #sys.exit(0)
info.close()
