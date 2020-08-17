#!/local/workspace/tools/anaconda2/bin/python2.7
import os
import struct
import sys
import numpy as np
import binascii
import argparse
import math
os.environ["GLOG_minloglevel"] = "1"
import caffe


np.set_printoptions(threshold='nan')
M = 9		#Qm.n
N = 7		#Qm.n
isQmn=True
#Little endian
def float_to_hex_binascii(f):
    return binascii.hexlify(struct.pack('<f', f))
#bintf = open("weights.bin", 'wb')
def write_bin(hex_string, bintf):
	hex_data = hex_string.decode("hex")
	bintf.write(hex_data)
#Big endian
def float_to_hex(f):
	t = f.astype(np.float16)
	#print "f32:", f, "(", type(f), ")", ", f16:", t, "(", type(t), ")"
	hx32 = hex(struct.unpack('<I', struct.pack('<f', f))[0])
	hx16 = hex(struct.unpack('<I', struct.pack('<f', t))[0])
	#print "H32:", hx32, ", H16:", hx16
	return hx16[2:] 
	#return f

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

def to16BitBin(number):
	#print "Number to convert:", number
	binary = '{0:016b}'.format(number)
	#print binary
	return binary

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

def byte_to_binary(n):
    return ''.join(str((n & (1 << i)) and 1) for i in reversed(range(8)))

def hex_to_binary_str(h):
    return ''.join(byte_to_binary(ord(b)) for b in binascii.unhexlify(h))

def hex_to_bin(h):
    #print h	
    return binascii.unhexlify(h)

def conv_layer_wtdata(data, tf):
	tf.write('Convolution weight data:\n')
	tf.write('Dimension:')
	num_output = data.shape[0]
	channels =  data.shape[1]
	kx =  data.shape[2]
	ky =  data.shape[3]
	tf.write('%d %d %d %d\n' % (num_output, channels, kx, ky))
	for no in range(num_output):
		nod = data[no]
		tf.write('Num output:%d\n' % no)
		for ch in range(channels):
			for x in range(kx):
				tf.write('\t\t')
				for y in range(ky):
					hex = float_to_hex(nod[ch][x][y])
					#tf.write('%f ' % nod[ch][x][y])
					tf.write('%s ' % hex)
				tf.write('\n')
			tf.write('\n')	
	tf.write('\n')		

def layer_biasdata(data, tf):
	tf.write('Bias data:\n')
	tf.write('Dimension:')
	dim = data.shape[0]
	tf.write('%d\n' % dim)
	for idx in range(dim):
		hex = float_to_hex(data[idx])
		#tf.write('%f ' % data[idx])
		tf.write('%s ' % hex)
	tf.write('\n')	
	
def ip_layer_wtdata(data, tf):
	dim1 = data.shape[0]
	dim2 = data.shape[1]
	tf.write('IP weight data:\n')
	tf.write('Dimension:')
	tf.write('%d %d\n' % (dim1, dim2))
	for i in data.shape:
		print " ", i
	print "\n"	
	for idx1 in range(dim1):
		for idx2 in range(dim2):
			hex = float_to_hex(data[idx1][idx2])
			#tf.write('%f ' % data[idx1][idx2])
			tf.write('%s ' % hex)
		tf.write('\n')
	tf.write('\n')	

def conv_layer_data_hex(weight, bias, tf, args, opchlist):
	print "Dumping Convolution Layer Data HEX Bias + Weight"
	#tf.write("#Conv Data:\n")
	bdim = bias.shape[0]
	chunks = 64
	first_bias_byte = 8
	remaining = chunks - first_bias_byte
	num_output = weight.shape[0]
	opchlist.append(num_output)
	channels =  weight.shape[1]
	if bdim != num_output:
		print "Bias dimension is not equal to number of weight outputs. Exiting."
		quit()
	bhex = "0x"
	bp1 = "00"
	bp2 = "00"
	bin=""
	print "Total to dump in each chunk:", chunks, " bytes"
	for bwidx in range(num_output):
		for ch in range(channels):
			if args.bias == "ZERO":
				bp1 = "00"
				bp2 = "00"
			elif args.bias == "ACT":	
				#if args.qmn:
				if isQmn:
					t = bias[bwidx]
					#print "Actual CB:", t
					qmn = toQmn(t, M, N)
					if t < 0:
						bin = twosComplementBin(qmn)
					else:
						bin = to16BitBin(qmn)
					bhex = bin2hex(bin)
				else :
					bhex = float_to_hex(bias[bwidx])
				#print "bhex:", bhex, ", bin:", bin
				bhex = bhex[:4]
				bp1 = bhex[:2]
				bp2 = bhex[2:]
			else:
				print "Wrong bias type. Using ZERO bias."
				bp1 = "00"
				bp2 = "00"
			#print "Bias: First ", 4 * 2, " bytes"	
			write_data_lsb_msb(tf, bp1, bp2, 4, args)		#Write first 4*2 byte bias
			nod = weight[bwidx][ch]
			wlen = write_conv_weights(nod, tf, args)
			#print "Weight: Next ", wlen * 2, " bytes"
			pad = remaining - (wlen*2)
			#print "Zero padding: Next ", pad, " bytes"
			if pad > 0:
				write_data_lsb_msb(tf, "00", "00", pad/2, args)		#Write last remaining bytes as ZERO padding 

def conv_layer_data_simfloat(weight, bias, tf, args, opchlist):
	print "Dumping Convolution Layer Data FLOAT Bias + Weight"
	tf.write("#Conv Data:\n")
	bdim = bias.shape[0]
	chunks = 64
	first_bias_byte = 8
	remaining = chunks - first_bias_byte
	num_output = weight.shape[0]
	opchlist.append(num_output)
	channels =  weight.shape[1]
	if bdim != num_output:
		print "Bias dimension is not equal to number of weight outputs. Exiting."
		quit()
	bp = 0.000
	print "Total to dump in each chunk:", chunks, " bytes"
	for bwidx in range(num_output):
		for ch in range(channels):
			if args.bias == "ZERO":
				bp = 0.000
			elif args.bias == "ACT":	
				bp = bias[bwidx]
			else:
				print "Wrong bias type. Using ZERO bias."
				bp = 0.000
			print "Bias: First ", 4, " lines"	
			write_data_float(tf, bp, 4)		#Write first 4 bytes bias
			nod = weight[bwidx][ch]
			wlen = write_conv_weights_float(nod, tf)
			print "Weight: Next ", wlen * 2, " lines"
			pad = remaining - (wlen*2)
			print "Zero padding: Next ", pad/2, " lines"
			if pad > 0:
				write_data_float(tf, 0.000, pad/2)		#Write last remaining bytes as ZERO padding 

def write_conv_weights(data, tf, args):
	kx =  data.shape[0]
	ky =  data.shape[1]
	whex = "0x"
	wp1 = "00"
	wp2 = "00"
	bin=""
	count = 0
	neg = 0
	for x in range(kx):
		for y in range(ky):
			#if args.qmn:
			if isQmn:
				t = data[x][y]
				#print "Actual CW:", t
				qmn = toQmn(t, M, N)
				if t < 0:
					bin = twosComplementBin(qmn)
				else:
					bin = to16BitBin(qmn)
				whex = bin2hex(bin)
			else :
				whex = float_to_hex(data[x][y])
			#print "whex:", whex, ", bin:", bin
			whex = whex[:4]
			wp1 = whex[:2]	#MSB
			wp2 = whex[2:]	#LSB
			write_data_lsb_msb(tf, wp1, wp2, 1, args)
			count = count + 1
	return count	

def write_conv_weights_float(data, tf):
	kx =  data.shape[0]
	ky =  data.shape[1]
	wh = 0.000
	count = 0
	for x in range(kx):
		for y in range(ky):
			t = data[x][y]
			wh = data[x][y]
			write_data_float(tf, wh, 1)
			count = count + 1
	return count	

def write_data_lsb_msb(tf, msb, lsb, n, args):	#Prints first LSB then MSB
	for i in range(n):
		if args.type == "SIMULATION":
			tf.write(msb)
			tf.write(lsb)
			tf.write('\n')
		elif args.type == "BOARD_HEX":	
			tf.write(lsb)	# 1 byte
			tf.write('\n')
			tf.write(msb)	# 1 byte
			tf.write('\n')
		elif args.type == "BOARD_BIN":	
			write_bin(lsb, tf)	
			write_bin(msb, tf)	
		else:
			print "Wrong type provided. SIMULATION/BOARD supported."
			quit()

def write_data_float(tf, data, bytes):
	for i in range(bytes):
		tf.write("%f" % data)
		tf.write('\n')

def ip_layer_data_hex_reorder(weight, bias, tf, args):		
	print "IP Layer data"
	numOutCh = weight.shape[0]
	print "Output channels:", numOutCh
	neurons = weight.shape[1]
	print "Neurons:", neurons
	nPE = 8
	sets = numOutCh / nPE
	if numOutCh % nPE > 0:
		sets = sets + 1
	print "Data sets:", sets
	print "Bias.shape:", bias.shape
	x2 = np.empty((neurons, sets, nPE), dtype=object)	#2 data sets, 8 PF
	#print x2
	currset = 0
	currdataidx = 0
	for bwidx in range(numOutCh):
		wtd=weight[bwidx]
		wx = wtd.shape[0]
		#print "wx:", wx
		for x in range(wx):
			t = wtd[x]
			#print "Actual IW:", t
			qmn = toQmn(t, M, N)
			if t < 0:
				bin = twosComplementBin(qmn)
			else:
				bin = to16BitBin(qmn)
			whex = bin2hex(bin)
			#print "whex:", whex, ", bin:", bin
			whex = whex[:4]
			#print whex, "currset:", currset, ", bwidx:", bwidx, ", x:", x, ", currdataidx:", currdataidx
			x2[x, currset, currdataidx ] = whex
		currdataidx = currdataidx + 1
		if currdataidx >= nPE:
			currdataidx = 0
			currset = currset + 1	

			#if bwidx < nPE:
			#	x2[x, 0, bwidx % nPE ] = whex	
			#else:
			#	x2[x, 1, bwidx % nPE ] = whex
	
	#print "#IP Data"
	#print x2	
	#tf.write("#IP Data\n")
	b = 0
	bshape = bias.shape[0]
	for st in range(sets):	
		for x in range(nPE):
			if b+x < bshape:
				bd = bias[b+x]
				#print "Actual IB:", bd
				bqmn = toQmn(bd, M, N)
				if bd < 0:
					bbin = twosComplementBin(bqmn)
				else:
					bbin = to16BitBin(bqmn)
				bhex = bin2hex(bbin)
				#print "bhex:", bhex, ", bin:", bbin
				bhex = bhex[:4]
				#tf.write(bhex)
				#tf.write("\n")
				bp1 = bhex[:2]
				bp2 = bhex[2:]
				write_data_lsb_msb(tf, bp1, bp2, 1, args)		#Write first 2 bytes bias
			else:
				#tf.write("0000\n")
				write_data_lsb_msb(tf, "00", "00", 1, args)		#Write first 2 bytes bias
		b = b + nPE	
		for x in range(neurons):
			for d in range(nPE):
				if x2[x, st, d] is None:
					#print "0000"
					#tf.write("0000\n")
					write_data_lsb_msb(tf, "00", "00", 1, args)		#Write first 2 bytes bias
				else:
					#print x2[x, st, d] 	
					#tf.write(x2[x, st, d])
					#tf.write("\n")
					wh = x2[x, st, d]
					bp1 = wh[:2]
					bp2 = wh[2:]
					write_data_lsb_msb(tf, bp1, bp2, 1, args)		#Write first 2 bytes bias
	
	
def ip_layer_data_hex(weight, bias, tf, args, opchlist, inW, inH):
	print "Dumping IP Layer Data HEX Bias + Weight"
	numIPCh = opchlist.pop()
	print "Input channels:", numIPCh
	numOutCh = weight.shape[0]
	print "Output channels:", numOutCh
	dim2 = weight.shape[1]
	opchlist.append(numOutCh)
	#print "dim2:", dim2
	#wtsize = (inW * inH * numIPCh + 1) * numOutCh * 2
	wtsize = (dim2 + 1) * numOutCh * 2
	tmp = math.ceil(numOutCh/8 + 0.00001)
	total = tmp * 8 * (dim2 + 1) * 2 
	numzero = total - wtsize
	print "WtSize:", wtsize, ", Total:", total, ", Num zero:", numzero
	bdim = bias.shape[0]
	if bdim != numOutCh:
		print "Bias dimension is not equal to number of output channel. Exiting.."
		quit()
	bhex="0x"
	bp1 = "00"
	bp2 = "00"
	wtlen = 0
	#tf.write("#IP Data:\n")	
	for bwidx in range(numOutCh):
		if args.bias == "ZERO":
			bp1 = "00"
			bp2 = "00"
		elif args.bias == "ACT":	
			#if args.qmn:
			if isQmn:
				t = bias[bwidx]
				#print "Actual IB:", t
				qmn = toQmn(t, M, N)
				if t < 0:
					bin = twosComplementBin(qmn)
				else:
					bin = to16BitBin(qmn)
				bhex = bin2hex(bin)
			else :
				bhex = float_to_hex(bias[bwidx])
			#print "bhex:", bhex, ", bin:", bin
			bhex = bhex[:4]
			bp1 = bhex[:2]
			bp2 = bhex[2:]
		else:
			print "Wrong bias type. Using ZERO bias."
			bp1 = "00"
			bp2 = "00"
		write_data_lsb_msb(tf, bp1, bp2, 1, args)		#Write first 2 bytes bias
		nod=weight[bwidx]
		wlen = write_ip_weights(nod, tf, args)  #wlen * 2 bytes weights
		wtlen = wtlen + (wlen*2+2)
	print "WTlen:", wtlen
	pad = int(total - wtlen)
	print "Zero pad:", pad
	if pad > 1:
		write_data_lsb_msb(tf, "00", "00", pad/2, args)

def ip_layer_data_simfloat(weight, bias, tf, args, opchlist, inW, inH):
	print "Dumping IP Layer Data FLOAT Bias + Weight"
	numIPCh = opchlist.pop()
	print "Input channels:", numIPCh
	numOutCh = weight.shape[0]
	print "Output channels:", numOutCh
	dim2 = weight.shape[1]
	opchlist.append(numOutCh)
	#print "dim2:", dim2
	wtsize = (dim2 + 1) * numOutCh * 2
	tmp = math.ceil(numOutCh/8 + 0.00001)
	total = tmp * 8 * (dim2 + 1) * 2 
	numzero = total - wtsize
	print "WtSize:", wtsize, ", Total:", total, ", Num zero:", numzero
	bdim = bias.shape[0]
	if bdim != numOutCh:
		print "Bias dimension is not equal to number of output channel. Exiting.."
		quit()
	bh=0.000
	wtlen = 0
	tf.write("#IP Data:\n")	
	for bwidx in range(numOutCh):
		if args.bias == "ZERO":
			bh = 0.000
		elif args.bias == "ACT":	
			bh = bias[bwidx]
		else:
			print "Wrong bias type. Using ZERO bias."
			bh = 0.000
		write_data_float(tf, bh, 1)		#Write first 2 bytes bias
		nod=weight[bwidx]
		wlen = write_ip_weights_float(nod, tf, args)  #wlen * 2 bytes weights
		wtlen = wtlen + (wlen*2+2)
	print "WTlen:", wtlen
	pad = int(total - wtlen)
	print "Zero pad:", pad
	if pad > 1:
		write_data_float(tf, 0.000, pad/2)

def write_ip_weights(data, tf, args):
	wx = data.shape[0]
	whex = "0x"
	wp1 = "00"
	wp2 = "00"
	count = 0
	for x in range(wx):
		#if args.qmn:
		if isQmn:
			t = data[x]
			#print "Actual IW:", t
			qmn = toQmn(t, M, N)
			if t < 0:
				bin = twosComplementBin(qmn)
			else:
				bin = to16BitBin(qmn)
			whex = bin2hex(bin)
		else :
			whex = float_to_hex(data[x])
		#print "whex:", whex, ", bin:", bin
		whex = whex[:4]
		wp1 = whex[:2]	#MSB
		wp2 = whex[2:]	#LSB
	 	write_data_lsb_msb(tf, wp1, wp2, 1, args)
	 	count = count + 1
	return count

def write_ip_weights_float(data, tf, args):
	wx = data.shape[0]
	wh = 0.000
	count = 0
	for x in range(wx):
		wh = data[x]
	 	write_data_float(tf, wh, 1)
	 	count = count + 1
	return count

def setQmn(val):
	global M
	global N
	print "Q", val
	splited=val.split('.', 2)
	M = int(splited[0])
	N = int(splited[1])
	print "M:", M, ", N:", N

def main(argv):
	parser = argparse.ArgumentParser()
	parser.add_argument('-w','--weights', help='caffemodel weights file', required=True)
	parser.add_argument('-p','--prototxt', help='prototxt file', required=True)
	parser.add_argument('-o','--output', help='output file', required=True)
	parser.add_argument('-b','--bias', help='bias to add (ZERO/ACT (default ZERO))', default='ZERO', required=False)
	parser.add_argument('-f','--outfmt', help='output format(HEX/TXT/SIMFLOAT (default HEX))', default='HEX', required=False)
	parser.add_argument('-t','--type', help='Type of output data for (SIMULATION/BOARD_HEX/BOARD_BIN (default SIMULATION))', default='SIMULATION', required=False)
	parser.add_argument('-q','--qmn', help="Convert to Qm.n (Default Q9.7)(NO : if not required)", default="9.7", required=False)
	args = parser.parse_args()
	print "Caffemodel Weights File:", args.weights
	print "Prototxt File:", args.prototxt
	print "Output File:", args.output
	print "Bias to Use:", args.bias
	print "Output Format:", args.outfmt
	print "Data Prepared For:", args.type
	print "Qm.n:", args.qmn
	if args.qmn == "NO":
		isQmn = False
	setQmn(args.qmn)
	#net = caffe.Net(MODEL_FILE, PRETRAIN_FILE, caffe.TEST)
	#net = caffe.Net(args.prototxt, args.caffemodel, caffe.TEST)
	net = caffe.Net(args.prototxt, 1, weights=args.weights)
	if args.type == "BOARD_BIN":
		tf = open(args.output, 'wb')
	else:	
		tf = open(args.output, 'w')

	outchannellist = [1]
	for param_name in net.params.keys():
		weight = net.params[param_name][0].data
		bias = net.params[param_name][1].data

		if args.outfmt == "TXT":
			if param_name.startswith("conv"):
				conv_layer_wtdata(weight, tf)
				layer_biasdata(bias, tf)
				#quit()
	
			if param_name.startswith("ip"):
				ip_layer_wtdata(weight, tf)
				layer_biasdata(bias, tf)
				#quit()
		elif args.outfmt == "HEX":
			if param_name.startswith("conv"):
				conv_layer_data_hex(weight, bias, tf, args, outchannellist)
			if param_name.startswith("ip1"):
				#ip_layer_data_hex(weight, bias, tf, args, outchannellist, 4, 4)
				ip_layer_data_hex_reorder(weight, bias, tf, args)
			if param_name.startswith("ip2"):
				#ip_layer_data_hex(weight, bias, tf, args, outchannellist, 1, 1)
				ip_layer_data_hex_reorder(weight, bias, tf, args)
		elif args.outfmt == "SIMFLOAT":		
			if param_name.startswith("conv"):
				conv_layer_data_simfloat(weight, bias, tf, args, outchannellist)
			if param_name.startswith("ip1"):
				ip_layer_data_simfloat(weight, bias, tf, args, outchannellist, 4, 4)
			if param_name.startswith("ip2"):
				ip_layer_data_simfloat(weight, bias, tf, args, outchannellist, 1, 1)
		else:
			print "Wrong \'outfmt\'..."
			quit()
	tf.close()
	
if __name__ == "__main__":
	main(sys.argv)
