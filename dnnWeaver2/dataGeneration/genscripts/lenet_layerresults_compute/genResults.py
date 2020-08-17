#!/local/workspace/tools/anaconda2/bin/python2.7

import os
import struct
import sys
import math
import numpy as np
import argparse
import random
import cnn_layers as cl
from StringIO import StringIO
import cv2
os.environ["GLOG_minloglevel"] = "1"
import caffe

np.set_printoptions(threshold=sys.maxsize)
np.set_printoptions(precision=3)
np.set_printoptions(suppress=True)
np.set_printoptions(linewidth=np.inf)


def create_padded_image(img, p, pt):
    ih = img.shape[0]
    iw = img.shape[1]
    nh = ih + (2 * p)
    nw = iw + (2 * p)
    new_img = np.zeros(shape=[1, nh, nw], dtype=np.uint8)
    for x in range(ih):
        for y in range(iw):
            val = img[x][y]
            if pt == 'SYM':
                new_img[0][x + p][y + p] = val
            elif pt == 'ASYM':    
                new_img[0][x][y] = val
            else:
                print "Wrong padding type. Using SYM padding..."
                new_img[0][x + p][y + p] = val
    return new_img     

def load_image(filename, ih, iw, p, pt):
    print "Loading image file:", filename
    img = cv2.imread(filename, 0)
    if img.shape != [ih, iw]:
        img2 = cv2.resize(img,(ih, iw))
        img = img2.reshape(ih, iw);
    else:
        img = img.reshape(ih, iw);
    image = create_padded_image(img, p, pt) 
    return image


def load_weights(weight_file, prototxt):
    net = caffe.Net(str(prototxt), 1, weights=str(weight_file))
    weights = {}
    print "Available layers:"
    for param_name in net.params.keys():
        weight = net.params[param_name][0].data
        print "\tParam:", param_name, ", Shape:", weight.shape
        weights[param_name] = weight
    return weights    
    
    
def load_weights_fc(filename, r, c):
    print "Loading weights file:", filename
    wtf = open(filename, "r")
    wts = np.zeros([r, c])
    idx = 0
    for line in wtf:
        #print line,
        c = StringIO(line)
        n = np.loadtxt(c)
        wts[idx] = n
        idx += 1
    return wts

def load_weights_cw1(filename):
    print "Loading weights file:", filename
    wtf = open(filename, "r")
    kw = 5
    kh = 5
    wts = np.zeros([1, 1, kh, kw])
    idx = 0
    for line in wtf:
        #print line,
        c = StringIO(line)
        n = np.loadtxt(c)
        wts[0][0][idx] = n
        idx += 1
    return wts

def load_weights_cw2(filename):
    print "Loading weights file:", filename
    wtf = open(filename, "r")
    kw = 5
    kh = 5
    wts = np.zeros([1, 1, kh, kw])
    idx = 0
    of = 0
    for line in wtf:
        #print line,
        if len(line) == 1:
            of += 1
            idx = 0
            continue
        c = StringIO(line)
        n = np.loadtxt(c)
        wts[of][0][idx] = n
        idx += 1
    return wts

def main(argv):
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-i','--image', help='Image file', required=True)
    parser.add_argument('-w','--weight_file', help='Caffemodel weight file', required=True)
    parser.add_argument('-ptxt','--prototxt', help='Caffe prototxt', required=True)
    parser.add_argument('-ih','--image_height', default=28, help='Image height', required=False)
    parser.add_argument('-iw','--image_width', default=28, help='Image width', required=False)
    parser.add_argument('-p','--padding', default=2, help='Required padding', required=False)
    parser.add_argument('-pt','--padding_type', default='SYM', help='Padding type(SYM/ASYM)', required=False)
    parser.add_argument('-qm','--qm', default=9, help='m of Qm.n', required=False)
    parser.add_argument('-qn','--qn', default=7, help='n of Qm.n', required=False)
    args = parser.parse_args()
    

    ih = int(args.image_height)
    iw = int(args.image_width)
    p = int(args.padding)
    pt = args.padding_type
    weight_file = args.weight_file
    prototxt = args.prototxt
    img_file = args.image
    m = int(args.qm)
    n = int(args.qn)

    print("*" * 50)
    print("All the image and weight data in this file are qmn equivalent decimal values")
    print("This data is used to validate the simulation results which is the result of qmn format operands")
    print("In simulation set signed decimal display format for the signals")
    print("*" * 50)
    image = load_image(img_file, ih, iw, p, pt)   
    image = image/255.0
    image = image * (2**n)
    image = image.astype('int64')
    print "Image shape:", image.shape
    print "Image:\n", image

    weights_pool = load_weights(weight_file, prototxt)
    print "Number of weight layers:", len(weights_pool)

    weights = weights_pool['conv1']
    weights = weights * (2**n)
    weights = weights.astype('int64')
    print "Conv1 weights shape:", weights.shape
    print "Loaded weights:\n", weights
    
    conv1 = cl.conv_op_3d(image, weights, stride = 1, pad = "VALID")
    conv1 = conv1.astype('int64')
    print "Conv1 output shape:", conv1.shape
    print "Conv1 output:\n"

    for o in range(conv1.shape[0]):
        for r in range(conv1.shape[1]):
            for c in range(conv1.shape[2]):
                print conv1[o][r][c],
            print "\n",
        print "\n",    
    
    pool1 = cl.max_pool_3d(conv1, kernel_size = 2, stride = 2)
    pool1 = pool1.astype('int64')
    print "Pool1 output shape:", pool1.shape
    print "Pool1 output:\n"
    for o in range(pool1.shape[0]):
        for r in range(pool1.shape[1]):
            for c in range(pool1.shape[2]):
                print pool1[o][r][c],
            print "\n",    
        print "\n",    

    #weights = load_weights_cw2(c2wt_file)
    weights = weights_pool['conv2']
    weights = weights * (2**n)
    weights = weights.astype('int64')
    print "Conv2 weights shape:", weights.shape
    print "Loaded weights:\n", weights
    conv2 = cl.conv_op_3d(pool1, weights, stride = 1, pad = "VALID")
    conv2 = conv2.astype('int64')
    print "Conv2 output shape:", conv2.shape
    print "Conv2 output:"
    for o in range(conv2.shape[0]):
        for r in range(conv2.shape[1]):
            for c in range(conv2.shape[2]):
                print conv2[o][r][c],
            print "\n",
        print "\n",    
    
    pool2 = cl.max_pool_3d(conv2, kernel_size = 2, stride = 2)
    pool2 = pool2.astype('int64')
    print "Pool2 output shape:", pool2.shape
    print "Pool2 output:"
    for o in range(pool2.shape[0]):
        for r in range(pool2.shape[1]):
            for c in range(pool2.shape[2]):
                print pool2[o][r][c],
            print "\n",   
        print "\n",    
   
    weights = weights_pool['fc1']
    weights = weights * (2**n)
    weights = weights.astype('int64')
    print "FC1 weights shape:", weights.shape
    print "FC1 weights:\n", weights
    flat = cl.flatten(pool2)
    fc1_out = cl.fully_connected_1d(flat, weights, weights.shape[0])
    fc1_out = fc1_out.astype('int64')
    print "FC1 output shape:", fc1_out.shape
    print "FC1 output:\n", fc1_out
    
    weights = weights_pool['fc2']
    weights = weights * (2**n)
    weights = weights.astype('int64')
    print "FC2 weights shape:", weights.shape
    print "FC2 weights:\n", weights
    fc2_out = cl.fully_connected_1d(fc1_out, weights, weights.shape[0])
    fc2_out = fc2_out.astype('int64')
    print "FC2 output shape:", fc2_out.shape
    print "FC2 output:\n", fc2_out
    fc2_out = fc2_out/2**(5*n)
    print "FC2 normal output:", fc2_out
    softm = cl.softmax(fc2_out)
    print "SoftMax output:", softm

if __name__ == "__main__":
    main(sys.argv)

