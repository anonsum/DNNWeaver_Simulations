#!/local/workspace/tools/anaconda2/bin/python2.7
####################################################
####  Dummy Weight generation script for DW2 #######
####################################################
import os
import struct
import sys
import math
import numpy as np
import argparse
import random

## format weight data in required MxN systolic array format for dw2
def genWtDataConv(sysarray, wt_list, tfd,tfh):
    #print "Number of weight matrices set(s):", len(wt_list)   
    #for mat in wt_list:
    #    print mat
    OPch = len(wt_list)    
    #print "Systolic array structure:"
    #print sysarray
    M = sysarray.shape[0]
    N = sysarray.shape[1]
    K = wt_list[0].shape[1]
    IPch = wt_list[0].shape[0]
    #print "Systolic array size (M x N):", M, " x ", N
    #print "Kernel size:", K
    #print "Number of output channel(s):", OPch
    #print "Number of input channel(s):", IPch
    outseti = OPch/M
    if OPch % M > 0:
        outseti = outseti + 1
    #print "Required Output Chunks:", outseti
    inseti = IPch/N
    if IPch % M > 0:
        inseti = inseti + 1
    #print "Required Input Chunks:", inseti
    for oc in range(outseti):
        for ic in range(inseti):
            for x in range(K):
                for y in range(K):
                    for m in range(M):
                        ocdx = oc*M + m
                        #print "ocdx:", ocdx
                        for n in range(N):
                            icdx = ic*N + n
                            #print "icdx:", icdx
                            if ocdx < len(wt_list):
                                mat = wt_list[ocdx]
                                #print "mat:", mat
                                if icdx < mat.shape[0]:
                                    layermat = mat[icdx]
                                    #print "layermat:", layermat
                                    val = layermat[x][y]
                                    sysarray[m][n] = val
                    #print "Systolic array:"
                    #print sysarray
                    t = np.transpose(sysarray)
                    #print "Trans:\n", t
                    c = np.reshape(t, M * N)
                    #print "Reshaped:", c
                    #print "Writing: ",
                    for l in range(M * N):
                        tfd.write("%d\n" % c[l])
                        tfh.write("%X\n" % c[l])
                    sysarray.fill(0) 
                

def fillarray(array, filler, startval, arrN):
    #print "Shape:", array.shape
    mval = 0	## used in mod filter 
    val = startval ## used in other filters 
    if filler == 'mod':
        for i in range(array.shape[0]):
            f = mval % arrN
            array[i].fill(f+1)
            mval = mval+1
    elif filler == 'inc':
	print "incremental filling of weight values.....\n"
	## fills the 5x5 array with incremental values from the startvalue 
	for i in range(array.shape[0]):	
	    #print("outer range",i) 
	    for j in range(array.shape[1]):	
	        for k in range(array.shape[2]):
            	    array[i,j,k]=(val)
	    	    #print(array)
        	    val = val + 1

    elif filler == 'rowinc':
	print "row increment and repeat for all rows....\n"
	## fills the 5x5 array with incremental values for an row . then repeat from startvalue again  
	for i in range(array.shape[0]):	
	    for j in range(array.shape[1]):	
		val=startval		## repeat for the rows 
	        for k in range(array.shape[2]):
            	    array[i,j,k]=(val)
	    	    #print(array)
        	    val = val + 1
    elif filler == 'const':
        for i in range(array.shape[0]):
            #f = val % array.shape[1]
            array[i].fill(val)
            val = val + 1
    elif filler == 'rand':
        for i in range(array.shape[0]):
            array[i].fill(random.randint(0, 3))
    else:
        print "Wrong filler type.."
        exit()

def fillarray_fc(array, filler, startval, arrN):
    
    if filler == 'inc':
        for i in range(arrN):
            array[i] = startval + i   
    elif filler == 'rand':
        array.fill(random.randint(0, 3))    
        
def genWtDataFC0(sysarray, wt_list, tfd, tfh):
    OPch = len(wt_list)    
    M = sysarray.shape[0]
    N = sysarray.shape[1]
    IPch = wt_list[0].shape[0]
    chunks = OPch/M
    if OPch % M > 0:
        chunks += 1
    for i in range(chunks):
        for e in range(IPch):
           for m in range(M):
                if i * M + m < OPch:
                    arr = wt_list[i * M + m]
                    val = arr[e]
                    sysarray[m][0] = val
           t = np.transpose(sysarray)
           c = np.reshape(t, M * N)
           for l in range(M * N):
               tfd.write("%d\n" % c[l])
               tfh.write("%X\n" % c[l])
           sysarray.fill(0) 

def genWtDataFC1(sysarray, wt_list, tfd, tfh):
    OPch = len(wt_list)    
    M = sysarray.shape[0]
    N = sysarray.shape[1]
    IPch = wt_list[0].shape[0]
    ichunks = OPch/N
    if OPch % N > 0:
        ichunks += 1
    ochunks = IPch/M
    if IPch % M > 0:
        ochunks += 1
    e = 0   
    for i in range(ichunks):    
        for o in range(ochunks):
                for m in range(M):
                    for n in range(N):
                        if i * N + n < OPch:
                            arr = wt_list[i * N + n]
                            if e < IPch:    
                                val = arr[e]
                                sysarray[m][n] = val
                    e += 1
                    if e >= IPch:
                        e = 0
                        break;   
                print sysarray
                #t = np.transpose(sysarray)
                #print "Transposed:\n", t
                c = np.reshape(sysarray, M * N)
                print "Reshaped:\n", c
                for l in range(M * N):
                    tfd.write("%d\n" % c[l])
                    tfh.write("%X\n" % c[l])
                sysarray.fill(0) 
        
def main(argv):
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-m','--row', default=4, help='Systolic array rows', required=False)
    parser.add_argument('-n','--col', default=4, help='Systolic array columns', required=False)
    parser.add_argument('-ic','--ip_channels', default=1, help='Number of output channels', required=False)
    parser.add_argument('-oc','--op_channels', default=1, help='Number of output channels', required=False)
    parser.add_argument('-k','--kernel', default=5, help='Kernel size', required=False)
    parser.add_argument('-l','--layer', default='conv', help='Layer name(conv/fc0/fc1)', required=False)
    parser.add_argument('-fill','--filler', default='inc', help='Weight matrix filler type(mod/inc/const/rand)', required=False)
    parser.add_argument('-stval','--startvalue', default=1, help='Specify the const or start value for inc', required=False)
    parser.add_argument('-out','--out_file', default='weights_layer.txt', help='Output file name', required=False)

    args = parser.parse_args()

    M = int(args.row)
    N = int(args.col)
    OPch = int(args.op_channels)
    IPch = int(args.ip_channels)
    K = int(args.kernel)
    filler = args.filler
    stval = args.startvalue
    layer = args.layer
    print "###############################################"
    print "Systolic array size (M x N):", M, " x ", N
    print "Number of input channel(s):", IPch
    print "Number of output channel(s):", OPch
    if layer == 'conv':
        print "Kernel size:", K
    print "Weight Matrix filler Type:", filler
    print "Filler Start value:",stval
    print "Layer:", layer
    print "###############################################"
    wt_list = []
   
    if layer == 'conv':
        np.random.seed(0)
        for i in range(OPch):
            wt = np.random.randint(1, size=(IPch, K, K))
	    ## Fill weight matrix with cont or incremental value or random 	
	    #startval = int(stval) +(i*10)
	    startval = int(stval) +(i*1)
            fillarray(wt, filler,int(startval),N)			 
            wt_list.append(wt)
   
        opcount = 0
        for mat in wt_list:
            print("Weight matrices (in dec) for output channel:{}\n".format(opcount+1))
            opcount = opcount + 1
            for i in range(mat.shape[0]):
                print mat[i]
        sysarray = np.zeros([M, N], dtype = int)    
        tfd = open(args.out_file, "w")
        hexfile = "hex_conv_" + str(args.out_file)	
        tfh = open(hexfile, "w")
        genWtDataConv(sysarray, wt_list, tfd,tfh)
        print ("\nGenerated dummy weights in systolic array format in {} {}".format(args.out_file,hexfile))
        tfd.close()
        tfh.close()
    elif layer == 'fc0':
        np.random.seed(0)
        for i in range(OPch):
            wt = np.random.randint(1, size=(IPch))
            startval = int(stval) +(i*1)
            fillarray_fc(wt, filler, int(startval),  IPch)			
            print "FC Wt:", wt
            wt_list.append(wt)
        sysarray = np.zeros([M, N], dtype = int)    
        tfd = open(args.out_file, "w")
        hexfile = "hex_fc0_" + str(args.out_file)	
        tfh = open(hexfile, "w")
        genWtDataFC0(sysarray, wt_list, tfd, tfh)
        print ("\nGenerated dummy weights in systolic array format in {} {}".format(args.out_file,hexfile))
        tfd.close()
        tfh.close()
    elif layer == 'fc1':
        np.random.seed(0)
        for i in range(OPch):
            wt = np.random.randint(1, size=(IPch))
            startval = int(stval) +(i*1)
            fillarray_fc(wt, filler, int(startval),  IPch)			
            print "FC Wt:", wt
            wt_list.append(wt)
        sysarray = np.zeros([M, N], dtype = int)    
        tfd = open(args.out_file, "w")
        hexfile = "hex_fc1_" + str(args.out_file)	
        tfh = open(hexfile, "w")
        genWtDataFC1(sysarray, wt_list, tfd, tfh)
        print ("\nGenerated dummy weights in systolic array format in {} {}".format(args.out_file,hexfile))
        tfd.close()
        tfh.close()
    else:
            assert 0
        

if __name__ == "__main__":
    main(sys.argv)
