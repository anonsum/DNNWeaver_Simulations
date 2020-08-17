#!/local/workspace/tools/anaconda2/bin/python2.7
import os
import struct
import sys
import math
import numpy as np
import argparse
import random
#import reorg_data as rd

def bin2hex(binstr):
	tmp = "{0:0>4X}".format(int(binstr, 2))
	return tmp

def to16BitBin(number):
	binary = '{0:016b}'.format(number)
	return binary

def genImageData(sysarray, in_list, tf, w, h):
    print "Number of image matrices(s)/ic:", len(in_list)   
    for mat in in_list:
        print mat
    IPch = len(in_list)    
    #print "Systolic array structure:"
    #print sysarray
    M = sysarray.shape[0]
    N = sysarray.shape[1]
    #print "Systolic array size (M x N):", M, " x ", N
    #print "Number of input channel(s):", IPch
    chunks = IPch/N
    if IPch % N > 0:
        chunks = chunks + 1
    #print "Required input channel chunks:", chunks
    for ic in range(chunks):
        for x in range(w):
            for y in range(h):
                for n in range(N):
                    icdx = ic * N + n
                    val = 0
                    if icdx < len(in_list):
                        mat = in_list[icdx]
                        val = mat[x][y]
                   #print val,
                    bin = to16BitBin(val)
                    hex = bin2hex(bin)
                    bhex = hex[:4]
                    tf.write("%s\n" % bhex)
                #print ""        

def fillarray(array, filler, count, startvalue):
    val = startvalue
    if filler == "const":
	#array.fill(val)
	for i in range(array.shape[0]):
	    array[i].fill(val)
	    #val = val + 1
    elif filler == 'inc':
	#print "incremental filling of image values.....\n"
	for i in range(array.shape[0]):	
	    for j in range(array.shape[1]):	
            	array[i,j]=(val)
            	val = val + 1
    elif filler == 'rand':
        array.fill(random.randint(0, 3))
    else:
        print "Wrong filler type.."
        exit()

def main(argv):
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-m','--row', default=4, help='Systolic array rows', required=False)
    parser.add_argument('-n','--col', default=4, help='Systolic array columns', required=False)
    parser.add_argument('-iw','--width', default=32, help='Image width', required=False)
    parser.add_argument('-ih','--height', default=32, help='Image height', required=False)
    parser.add_argument('-ic','--ip_channels', default=1, help='Number of output channels', required=False)
    parser.add_argument('-fill','--filler', default='inc', help='Weight matrix filler type(const|inc|rand)', required=False)
    parser.add_argument('-stval','--startvalue', default=1, help='Specify the const or start value for inc', required=False)
    parser.add_argument('-out','--out_file', default='input_image.txt', help='Output file name', required=False)
    args = parser.parse_args()

    M = int(args.row)
    N = int(args.col)
    IPch = int(args.ip_channels)
    filler = args.filler
    w = int(args.width)
    h = int(args.height)
    stval = int(args.startvalue)
    print "###############################################"
    print "Systolic array size (M x N):", M, " x ", N
    print "Image size:(W x H):" , w , "x", h  
    print "Number of input channels:", IPch
    print "Data filler Type:", filler
    print "###############################################"
    in_list = []
    
    np.random.seed(0)

    image_d = np.random.randint(1, size=(IPch, h, w))
    for i in range(IPch):
        image = image_d[i]
        fillarray(image, filler, len(in_list),stval)
        stval = stval + 1; 
  
    print "Generated:\n", image_d

    #new_org = rd.reorganize_data(image_d, M, N)
   # image_d = new_org
    image_d = image_d.astype('int32')
    
    image_p = np.random.randint(1, size=(IPch, h+2, w+2))
    for i in range(IPch):
        for r in range(h):
            for c in range(w):
	        image_p[i][r][c] = image_d[i][r][c]
    image_d = image_p	
    print "Reorganized:\n", image_d
    for i in range(IPch):
        image = image_d[i]
        in_list.append(image)

    sysarray = np.zeros([M, N], dtype = int)    
    tf = open(args.out_file, "w")
    genImageData(sysarray, in_list, tf, w + 2, h + 2)

    print "\nGenerated image data for systolic array format in <", args.out_file, ">"

    tf.close()

if __name__ == "__main__":
    main(sys.argv)
