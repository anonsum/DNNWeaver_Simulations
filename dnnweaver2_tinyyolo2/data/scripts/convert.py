#!/local/workspace/tools/anaconda3/envs/tfpy36cpuenv/bin/python
import sys
import os
import binascii as ba
import argparse


def convert_to_bin(argv):
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-i','--infile', help='Input hex file', required=True)
    parser.add_argument('-o','--outfile', default='converted.bin', help='Output file name', required=False)
    args = parser.parse_args()
    inp = open(args.infile, "r")
    outp = open(args.outfile, "wb")
   
    nline = 0 
    for line in inp:
        line = line.rstrip()
        if len(line) == 0:
            continue
        print("Line:{}, Len:{}".format(line, len(line)))
        strr = line[2:] + line[0:2]
        bindata = ba.unhexlify(strr)
        outp.write(bindata)
        nline = nline + 1
    print ("Number of bytes written:{} bytes".format(nline*2))
    inp.close()
    outp.close()
    
if __name__ == "__main__":
    convert_to_bin(sys.argv)
