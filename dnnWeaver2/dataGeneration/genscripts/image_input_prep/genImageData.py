#!/local/workspace/tools/anaconda2/bin/python2.7
## script to generate input image data in qmn format. 

import os
import struct
import sys
import numpy as np
import argparse
import cv2


def copy_img28_2_img32_asym(img28, img32, p):
    print "Using assymetric padding..."
    w = img28.shape[0]
    h = img28.shape[1]
    for x in range(h):
        for y in range(w):
            val = img28[x][y]
            img32[x][y] = val

def copy_img28_2_img32_sym(img28, img32, p):
    print "Using symetric padding..."
    w = img28.shape[0]
    h = img28.shape[1]
    for x in range(h):
        for y in range(w):
            val = img28[x][y]
            img32[x + p][y + p] = val

def print_img(img):
    w = img.shape[0]
    h = img.shape[1]
    for x in range(h):
        for y in range(w):
            val = img[x][y]
            print val,
        print "\n",

def print_zeros(tf, n):
    for i in range(n):
        tf.write("%s\n" % "0000")

def toQmn(number, m, n):
	prod = int(number * (2 ** n))
	return prod

def bin2hex(binstr):
	tmp = "{0:0>4X}".format(int(binstr, 2))
	return tmp

def to16BitBin(number):
	binary = '{0:016b}'.format(number)
	return binary

def main(argv):
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-i','--infile', help='Input file', required=True)
    parser.add_argument('-o','--outfile', help='Output file', required=True)
    parser.add_argument('-iw','--in_width', default=28, help='Input image width', required=False)
    parser.add_argument('-ih','--in_height', default=28, help='Input image height', required=False)
    parser.add_argument('-pt','--pad_type', default='SYM', help='Padding type(ASYM/SYM)', required=False)
    parser.add_argument('-p','--padding', default=2, help='Padding value', required=False)
    parser.add_argument('-m','--qm', default=9, help='m of Qm.n', required=False)
    parser.add_argument('-n','--qn', default=7, help='n of Qm.n', required=False)
    args = parser.parse_args()
    print "Input file:", args.infile
    print "Output file:", args.outfile
    iw = int(args.in_width)
    ih = int(args.in_height)
    p = int (args.padding)
    qm = int (args.qm)
    qn = int (args.qn)
    print ("Expected input image shape: %d x %d. Original input will be resized if not as expected." % (ih, iw)) 
    print ("Input image (%d x %d) will be padded by (%d x %d) pixels" % (ih, iw, p * 2, p * 2))
    img = cv2.imread(args.infile, -1)
    if img.shape != [ih, iw]:
        img2 = cv2.resize(img,(ih, iw))
        img = img2.reshape(ih, iw, -1);
    else:
        img = img.reshape(ih, iw,-1);
    img2 = img
    print "Input image shape after processing:", img2.shape
    nh = ih + (p * 2)
    nw = iw + (p * 2)
    img32 = np.zeros(shape=[nh, nw], dtype=np.uint8)
    if args.pad_type == 'ASYM':
        copy_img28_2_img32_asym(img2, img32, p)
    elif args.pad_type == 'SYM':    
        copy_img28_2_img32_sym(img2, img32, p)
    else:
        print "Wrong padding type. Using symmetric padding.."    
        copy_img28_2_img32_sym(img2, img32, p)

    w = img32.shape[0]
    h = img32.shape[1]
    img32 = img32/255.0
    outfile = args.outfile
    ind = outfile.rfind('.')
    if ind != -1:
        p1 = outfile[0:ind]
    else:
        p1 = outfile

    out = open(outfile, 'w')
    txtimg = open(p1 + "_qmn_2d.hex", 'w')
    txtimg_dec = open(p1 + "_qmn_2d.dec", 'w')
    print "Converted to image shape:", img32.shape
    for x in range(h):
        for y in range(w):
            val = img32[x][y]
            qmn = toQmn(val, qm, qn)
            bin = to16BitBin(qmn)
            hex = bin2hex(bin)
            bhex = hex[:4]
            out.write("%s\n" % (bhex))
            txtimg.write("%s " % bhex)
            txtimg_dec.write("%3d " % qmn)
            #print "Pixel:", val, ", Q9.7:", qmn, ":", bhex
            print_zeros(out, 3)
        txtimg.write("\n")
        txtimg_dec.write("\n")
    print "Formatted data to use to run DW2 : ", outfile
    print "Pixel data in 2D decimal format:", p1 + "qmn_2d.dec"
    print "Pixel data in 2D hex format:", p1 + "qmn_2d.hex"

if __name__ == "__main__":
    main(sys.argv)
