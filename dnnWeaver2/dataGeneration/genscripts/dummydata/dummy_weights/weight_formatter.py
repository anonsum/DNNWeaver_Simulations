#!/local/workspace/tools/anaconda2/bin/python2.7
#############################################################
####  Memory weight pattern generation script for DW2 #######
#############################################################
import os
import struct
import sys
import math
import numpy as np
import argparse
import random
import conversions as cv

##################################################
## Merge the weights in 1D format and reshape it##
## again to 3D shape [ic X k X k]               ##
##################################################

def reorganize_wts(weights, k):
    #print "Weights to reorganize:\n", weights
    nICs = len(weights)
    nElems = len(weights[0])
    #print "Number of weights:", nICs
    #print "Total elements:", nICs * nElems
    merged = np.zeros([nICs * nElems])
    n = 0
    for e in range(nElems):
        for i in range(nICs):
            val = weights[i][e]
            merged[n] = val
            n += 1
    #print "1D merged:\n", merged        
    merged = np.reshape(merged, [nICs, k, k])        
    return merged        

###################################################
## Reorganize the convolution weights. Increases ##
## number of ICs if input number ICs is more than##
## N of M x N systolic array size. This id used  ##
## when number of ICs is greater that N of M x N ##
## systolic array.                               ##   
###################################################

def reorganize_cw_increase(weights, M, N):
    ic = weights.shape[0]
    k  = weights.shape[1]
    ichunks = ic/N
    if ic % N > 0:
        ichunks += 1
    #print "Number of computation sets:", ichunks

    tmp = np.zeros([ichunks, k, k])
    tmp_ics = np.zeros([ichunks * N, k, k])
  
    ics_processed = {}
    weights_to_process = []
    ics_to_process = []
    for i in range(ic):
        if not ics_processed.has_key(i):
            for n in range(ichunks):
                rel_idx = i%N
                abs = n * N + rel_idx
                ics_to_process.append(abs)
                ics_processed[abs] = 1
                if abs < ic:
                    weights_to_process.append(weights[abs].flatten())
                else:
                    weights_to_process.append(np.zeros([k *  k]))   
            merged = reorganize_wts(weights_to_process, k)
            for l in range(len(ics_to_process)):
                tmp_ics[ics_to_process[l]] = merged[l]
            del weights_to_process[:]
            del ics_to_process[:]
    return tmp_ics


################################################
## Reorganize convolution weights when number ##
## of ICs is less than or equal to N of M x N ##
## systolic array                             ##  
################################################

def reorganize_cw(weights, M, N):
    ic = weights.shape[0]
    k  = weights.shape[1]
    ichunks = ic/N
    if ic % N > 0:
        ichunks += 1
    #print "Number of computation sets:", ichunks

    tmp = np.zeros([ichunks, k, k])
    tmp_ics = np.zeros([ic, k, k])
  
    ics_processed = {}
    weights_to_process = []
    ics_to_process = []
    for i in range(ic):
        if not ics_processed.has_key(i):
            for n in range(ichunks):
                rel_idx = i%N
                abs = n * N + rel_idx
                if abs < ic:
                    ics_to_process.append(abs)
                    ics_processed[abs] = 1
                    weights_to_process.append(weights[abs].flatten())
                else:
                    weights_to_process.append(np.zeros([k *  k]))   
            merged = reorganize_wts(weights_to_process, k)
            for l in range(len(ics_to_process)):
                if ics_to_process[l] < ic:
                    tmp_ics[ics_to_process[l]] = merged[l]
            del weights_to_process[:]
            del ics_to_process[:]
    return tmp_ics

#########################################################
## Reorganize convolution weights. Creates interleaved ##
## memory pattern.                                     ## 
#########################################################

def reorganize_conv_weights(name, weights, M, N):
    #print "Reorganizing:", name
    #print "Systolic array size: ", M, "x", N
    #print "Weights shape:", weights.shape
    oc = weights.shape[0]
    ic = weights.shape[1]
    k  = weights.shape[2]
    weight_list = []
    for o in range(oc):
        if ic > N:
            weight_list.append(reorganize_cw_increase(weights[o], M, N))
        else:
            weight_list.append(reorganize_cw(weights[o], M, N))

    noc = len(weight_list)
    nic = weight_list[0].shape[0]
    new_array = np.zeros([noc, nic, k, k])
    for i in range(noc):
        new_array[i] = weight_list[i]

    return new_array

##############################################################################
##Unflatten the flattened FC weights.                                       ##
##Inputs:                                                                   ##
##  weights             : weights numpy array                               ##
##  conv2_num_output    : Just previous convolution layer's number of output##
##  conv2_k             : Kernel size of just previous convolution layer    ##
##############################################################################

def unflattened_fc0_weights(weights, conv2_num_output, conv2_k):
    #print "FC0  weights shape:", weights.shape
    oc = weights.shape[0]
    new_array = np.zeros([oc, conv2_num_output, conv2_k, conv2_k])
    for o in range(oc):
        n = np.reshape(weights[o], [conv2_num_output, conv2_k, conv2_k])
        new_array[o] = n
    return new_array    

######################################################################
## Format weight data in required MxN systolic array format for dw2.##
######################################################################

def genWtDataConv(sysarray, wt_list, tff, tfh, tfd, qm, qn):
    OPch = len(wt_list)    
    M = sysarray.shape[0]
    N = sysarray.shape[1]
    K = wt_list[0].shape[1]
    IPch = wt_list[0].shape[0]
    outseti = OPch/M
    if OPch % M > 0:
        outseti = outseti + 1
    inseti = IPch/N
    if IPch % M > 0:
        inseti = inseti + 1
    for oc in range(outseti):
        for ic in range(inseti):
            for x in range(K):
                for y in range(K):
                    for m in range(M):
                        ocdx = oc*M + m
                        for n in range(N):
                            icdx = ic*N + n
                            if ocdx < len(wt_list):
                                mat = wt_list[ocdx]
                                if icdx < mat.shape[0]:
                                    layermat = mat[icdx]
                                    val = layermat[x][y]
                                    sysarray[m][n] = val
                    t = np.transpose(sysarray)
                    c = np.reshape(t, M * N)
                    for l in range(M * N):
                        tff.write("%f\n" % cv.toQmnFloat(c[l], qm, qn))
                        tfh.write("%s\n" % cv.toQmnHex(c[l], qm, qn))
                        tfd.write("%s\n" % cv.toDecHex(c[l]))
                    sysarray.fill(0) 
        

############################################################
## Creates memory data pattern for second FC layer onward.##
############################################################

def genWtDataFC1(sysarray, wt_list, tff, tfh, qm, qn):
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
                c = np.reshape(sysarray, M * N)
                for l in range(M * N):
                    tff.write("%f\n" % cv.toQmnFloat(c[l], qm, qn))
                    tfh.write("%s\n" % cv.toQmnHex(c[l], qm, qn))
                sysarray.fill(0)

