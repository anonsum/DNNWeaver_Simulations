#!/local/workspace/tools/anaconda2/bin/python2.7
## script to process layer weights and format as needed for dnnweaver2 

import os
import struct
import sys
import numpy as np
import binascii
import argparse
import math
#import bitstring
os.environ["GLOG_minloglevel"] = "1"
import caffe
np.set_printoptions(threshold=sys.maxsize)
np.set_printoptions(precision=3)
np.set_printoptions(suppress=True)
np.set_printoptions(linewidth=np.inf)
import weight_formatter as wf

def main(argv):
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-w','--weights', help='Caffemodel weights file', required=True)
    parser.add_argument('-p','--prototxt', help='Prototxt file', required=True)
    parser.add_argument('-model','--modelname', default="model", help='cnn model name', required=False)
    #parser.add_argument('-o','--out_file', help='Output file', required=True)
    parser.add_argument('-M','--row', default=4, help='Systolic array rows', required=False)
    parser.add_argument('-N','--col', default=4, help='Systolic array columns', required=False)
    parser.add_argument('-m','--qm', default=9, help='m of Qm.n', required=False)
    parser.add_argument('-n','--qn', default=7, help='n of Qm.n', required=False)
    
    args = parser.parse_args()
    print ("*" * 50)
    print "Caffemodel Weights File :", args.weights
    print "Prototxt File	   :", args.prototxt
    print "CNN model name	   :", args.modelname
    print ("*" * 50)
    #print "Output File:", args.out_file
    M = int(args.row)
    N = int(args.col)
    
    qm = int(args.qm)
    qn = int(args.qn)
    ochs = []

    net = caffe.Net(args.prototxt, 1, weights=args.weights)
    for param in net.params.keys():
        ochs.append(net.params[param][0].shape[0])
    ochstr = '_'.join([str(elem) for elem in ochs])
    ochstr = args.modelname + "_" + ochstr 
    out_dir = 'weightdata/' + ochstr + '/'   
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    last_conv_oc = -1
    last_conv_k = -1
    last_layer = "NONE"
    for param_name in net.params.keys():
        weight = net.params[param_name][0].data
        print "\nLayer Name:", param_name, ", Shape:", weight.shape
        if param_name.startswith("conv"):
            new_array = wf.reorganize_conv_weights(param_name, weight, M, N)
            weight = new_array
            sysarray = np.zeros([M, N], dtype = float)
            floatfile = out_dir + param_name + ".float"
            tff = open(floatfile, "w")
            hexfile = out_dir + param_name + ".hex"
            tfh = open(hexfile, "w")
            wt_list = []
            for i in range(weight.shape[0]):
                wt_list.append(weight[i])
            last_conv_oc = weight.shape[0]
            last_conv_k = weight.shape[2]
            last_layer = "conv"
            wf.genWtDataConv(sysarray, wt_list, tff, tfh, qm, qn)
            print ("Generated weights in systolic array format in {} {}".format(floatfile, hexfile))
            tff.close()
            tfh.close()
        elif param_name.startswith("fc1") and last_layer == "conv":
            sysarray = np.zeros([M, N], dtype = float)
            floatfile = out_dir + param_name + ".flt"
            tff = open(floatfile, "w")
            hexfile = out_dir + param_name + ".hex"
            tfh = open(hexfile, "w")
            wt_list = []
            unflattened = wf.unflattened_fc0_weights(weight, last_conv_oc, last_conv_k) #conv2 num_output = 50, kernel_size = 5
            weight = wf.reorganize_conv_weights(param_name, unflattened, M, N)
            for i in range(weight.shape[0]):
                wt_list.append(weight[i])
            wf.genWtDataConv(sysarray, wt_list, tff, tfh, qm, qn)
            print ("Generated weights in systolic array format in {} {}".format(floatfile, hexfile))
            tff.close()
            tfh.close()
        elif param_name.startswith("fc2"):
            sysarray = np.zeros([M, N], dtype = float)
            floatfile = out_dir + param_name + ".flt"
            tff = open(floatfile, "w")
            hexfile = out_dir + param_name + ".hex"
            tfh = open(hexfile, "w")
            wt_list = []
            oc = weight.shape[0]
            ic = weight.shape[1]
            for i in range(oc):
                wt_list.append(weight[i])
            wf.genWtDataFC1(sysarray, wt_list, tff, tfh, qm, qn)
            print ("Generated weights in systolic array format in {} {}".format(floatfile, hexfile))
            tff.close()
            tfh.close()
        else:
            print "Layer <", param_name, "> not handled..."
     
if __name__ == "__main__":
    main(sys.argv)
