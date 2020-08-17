#!/local/workspace/tools/anaconda2/bin/python2.7
import os
import struct
import sys
import numpy as np
import binascii
import argparse
import math
#import bitstring
os.environ["GLOG_minloglevel"] = "1"

#Big endian
def float_to_hex(f):
    t = f.astype(np.float16)
    #print "f32:", f, "(", type(f), ")", ", f16:", t, "(", type(t), ")"
    hx32 = hex(struct.unpack('<I', struct.pack('<f', f))[0])
    hx16 = hex(struct.unpack('<I', struct.pack('<f', t))[0])
    #print "H32:", hx32, ", H16:", hx16
    return hx16[2:] 
    #return f

def fill_zeros(no, tf):
    for i in range(no):
        tf.write("0000\n")

def to16BitBin(number):
	binary = '{0:016b}'.format(number)
	return binary

def toQmn(number, m, n):
	#print "Number to convert:", number
	#print "Qm.n","==>", m, ".", n
	prod = int(number * (2 ** n))
	#print prod
	return prod

def bin2hex(binstr):
	#tmp = hex(int(binstr, 2))
	tmp = "{0:0>4X}".format(int(binstr, 2))
	#tmp = tmp[2:]
	return tmp

def twosComplementBin(number):
    if number == 0:
        return "0000000000000000"
    binint = '{0:016b}'.format(number) #convert to binary
    tc = findTwoscomplement(binint)
    return tc

def findTwoscomplement(str): 
    n = len(str) 
    # Traverse the string to get first  
    # '1' from the last of string 
    i = n - 1
    while(i >= 0): 
        if (str[i] == '1'): 
            break
        i -= 1
    # If there exists no '1' concatenate 1  
    # at the starting of string 
    if (i == -1): 
        return '1'+str
    # Continue traversal after the  
    # position of first '1' 
    k = i - 1
    while(k >= 0): 
        # Just flip the values 
        if (str[k] == '1'): 
            str = list(str) 
            str[k] = '0'
            str = ''.join(str) 
        else: 
            str = list(str) 
            str[k] = '1'
            str = ''.join(str) 
        k -= 1
    # return the modified string 
    return str

def toQmnHex(d, m, n):
    qmn = toQmn(d, 9, 7)
    #print "Q9.7:", qmn, ",",
    if d < 0:
        bin = twosComplementBin(qmn)
        #print "TC:", bin, ",",
    else:
        bin = to16BitBin(qmn)
    hex = bin2hex(bin)
    return hex
 
def toQmnFloat(d, m, n):
    qmn = toQmn(d, 9, 7)
    return qmn
