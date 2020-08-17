#!/local/workspace/tools/anaconda2/bin/python2.7
import os
import struct
import sys
import numpy as np
import argparse
import cv2

M = 9
N = 7
isQmn=True

def write_bin(hex_string, bintf):
    hex_data = hex_string.decode("hex")
    bintf.write(hex_data)

def toQmn(number, m, n):
	#print "Number to convert:", number
	#print "Qm.n","==>", m, ".", n
	prod = int(number * (2 ** n))
	#print prod
	return prod

def bin2hex(binstr):
	tmp = "{0:0>4X}".format(int(binstr, 2))
	#print "Hex:", tmp
	return tmp

def to16BitBin(number):
	#print "Number to convert:", number
	binary = '{0:016b}'.format(number)
	#print binary
	return binary

def write_data_lsb_msb(outf, msb, lsb, n, args):	#Prints first LSB then MSB
	for i in range(n):
		if args.type == "SIMULATION":
			outf.write(msb)
			outf.write(lsb)
			outf.write('\n')
		elif args.type == "BOARD_HEX":	
			outf.write(lsb)	# 1 byte
			outf.write('\n')
			outf.write(msb)	# 1 byte
			outf.write('\n')
		elif args.type == "BOARD_BIN":	
			write_bin(lsb, outf)
			write_bin(msb, outf)
		
		else:
			print "Wrong type provided. SIMULATION/BOARD supported."
			quit()

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
	parser.add_argument('-i','--infile', help='Input file', required=True)
	parser.add_argument('-o','--outfile', help='Output file', required=True)
	parser.add_argument('-t','--type', help='Output type(SIMULATION/BOARD_HEX/BOARD_BIN (default SIMULATION))', default='SIMULATION', required=False)
	parser.add_argument('-q','--qmn', help="Convert to Qm.n (Default Q9.7)(NO : if not required)", default="9.7", required=False)
	args = parser.parse_args()
	print "Input file:", args.infile
	print "Output file:", args.outfile
	print "Qm.n:", args.qmn
	if args.qmn == "NO":
		isQmn = False
	setQmn(args.qmn)
	chunk = 64
	padding = 8
	img = cv2.imread(args.infile, -1)
	if img.shape != [28,28]:
	    img2 = cv2.resize(img,(28,28))
	    img = img2.reshape(28,28,-1);
	else:
	    img = img.reshape(28,28,-1);
	img = img/256.0
	print type(img)
	w = img.shape[0]
	h = img.shape[1]
	tf = open("temp.txt", 'w')
	if args.type == "BOARD_BIN":
		out = open(args.outfile, 'wb')
	else:
		out = open(args.outfile, 'w')
	#print img
	print "Rows:", h
	print "Cols:", w
	for x in range(h):
		for y in range(w):
			val = img[x][y]
			qnm = toQmn(val, M, N)
			bin = to16BitBin(qnm)
			hex = bin2hex(bin)
			tf.write("%f " % img[x][y])
			#out.write(hex)
			#out.write("\n")
			bhex = hex[:4]
			bp1 = bhex[:2]
			bp2 = bhex[2:]
			write_data_lsb_msb(out, bp1, bp2, 1, args)
		for i in range(padding/2):
			#out.write("0000\t#padding\n")
			write_data_lsb_msb(out, "00", "00", 1, args)
		tf.write("\n")

	#cv2.imwrite(args.outfile, img)


if __name__ == "__main__":
	main(sys.argv)
