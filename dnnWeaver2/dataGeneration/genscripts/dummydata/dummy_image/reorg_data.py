import os
import struct
import sys
import math
import numpy as np
import argparse
import random


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

def reorganize_cw_increase(weights, M, N):
    ic = weights.shape[0]
    k  = weights.shape[1]
    ichunks = ic/N
    if ic % N > 0:
        ichunks += 1
    #print "Number of computation sets:", ichunks
    #print "Weights shape:", weights.shape
    #print "Weights before reorganizing:\n", weights

    tmp = np.zeros([ichunks, k, k])
    tmp_ics = np.zeros([ichunks * N, k, k])
    #print "TMP array shape:", tmp.shape
  
    ics_processed = {}
    weights_to_process = []
    ics_to_process = []
    for i in range(ic):
        #print "IC:", i
        if not ics_processed.has_key(i):
            for n in range(ichunks):
                rel_idx = i%N
                abs = n * N + rel_idx
                #print "Rel:", rel_idx, ", Abs:", abs,
                #print "ICs:", abs
                ics_to_process.append(abs)
                ics_processed[abs] = 1
                if abs < ic:
                    #weights_to_process.append(np.reshape(weights[abs], k * k))
                    weights_to_process.append(weights[abs].flatten())
                else:
                    weights_to_process.append(np.zeros([k *  k]))   
            merged = reorganize_wts(weights_to_process, k)
            for l in range(len(ics_to_process)):
                tmp_ics[ics_to_process[l]] = merged[l]
            del weights_to_process[:]
            del ics_to_process[:]
            #print "Merged:\n", merged
    return tmp_ics

def reorganize_cw(weights, M, N):
    ic = weights.shape[0]
    k  = weights.shape[1]
    ichunks = ic/N
    if ic % N > 0:
        ichunks += 1
    #print "Number of computation sets:", ichunks
    #print "Weights shape:", weights.shape
    #print "Weights before reorganizing:\n", weights

    tmp = np.zeros([ichunks, k, k])
    tmp_ics = np.zeros([ic, k, k])
    #print "TMP array shape:", tmp.shape
  
    ics_processed = {}
    weights_to_process = []
    ics_to_process = []
    for i in range(ic):
        #print "IC:", i
        if not ics_processed.has_key(i):
            for n in range(ichunks):
                rel_idx = i%N
                abs = n * N + rel_idx
                #print "Rel:", rel_idx, ", Abs:", abs,
                #print "ICs:", abs
                if abs < ic:
                    ics_to_process.append(abs)
                    ics_processed[abs] = 1
                    weights_to_process.append(weights[abs].flatten())
                else:
                    weights_to_process.append(np.zeros([k *  k]))   
            merged = reorganize_wts(weights_to_process)
            for l in range(len(ics_to_process)):
                if ics_to_process[l] < ic:
                    tmp_ics[ics_to_process[l]] = merged[l]
            del weights_to_process[:]
            del ics_to_process[:]
            #print "Merged:\n", merged
    return tmp_ics


def reorganize_data(weights, M, N):
    #print "Systolic array size: ", M, "x", N
    #print "Weights shape:", weights.shape
    ic = weights.shape[0]
    k  = weights.shape[1]
    #new_array = np.zeros([oc, ic, k, k])
    #print "New array shape:", new_array.shape
    weight_list = []
    if ic > N:
        weight_list.append(reorganize_cw_increase(weights, M, N))
    else:
        weight_list.append(reorganize_cw(weights, M, N))

    noc = len(weight_list)
    print noc, weight_list[0].shape[0], weight_list[0].shape[1], weight_list[0].shape[2]
    nic = weight_list[0].shape[0]
    k = weight_list[0].shape[1]

    new_array = np.zeros([noc, nic, k, k])
    for i in range(noc):
        new_array[i] = weight_list[i]
    
    return new_array[0]

