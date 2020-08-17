####################################################
caffe2bin.py: Converts caffemodel weight file to HEX text format.
##################################################


usage: caffe2bin.py [-h] -w WEIGHTS -p PROTOTXT -o OUTPUT [-b BIAS]
                    [-f OUTFMT] [-t TYPE] [-q QMN]


optional arguments:
  -h, --help            show this help message and exit
  -w WEIGHTS, --weights WEIGHTS
                        caffemodel weights file
  -p PROTOTXT, --prototxt PROTOTXT
                        prototxt file
  -o OUTPUT, --output OUTPUT
                        output file
  -b BIAS, --bias BIAS  bias to add (ZERO/ACT (default ZERO))
  -f OUTFMT, --outfmt OUTFMT
                        output format(HEX/TXT/SIMFLOAT (default HEX))
  -t TYPE, --type TYPE  Type of output data for
                        (SIMULATION/BOARD_HEX/BOARD_BIN (default SIMULATION))
  -q QMN, --qmn QMN     Convert to Qm.n (Default Q9.7)(NO : if not required)


Few short description:

-b [ZERO/ACT] : Bias value to be used.
				ZERO : Bias value will be ZERO
				ACT  : Actual bias value will be used

-f [HEX/TXT/SIMFLOAT] : Data format for output.
						HEX : Hexadecimal format
						TXT : Text matrix format (Mainly to debug)
						SIMFLOAT : Float value in simulation format (Mainly for debug)

-t [SIMULATION/BOARD_HEX/BOARD_BIN] : Data required for.
					    SIMULATION : Data for simulation testing.
						BOARD_HEX  : Data for actual board testing in hex format.
						BOARD_BIN  : Data for actual board testing in binary format.

 
Example:
   caffe2bin.py -w <caffemodel file> -p <net prototxt> -o <output file> -b ACT -t SIMULATION 
   caffe2bin.py -w <caffemodel file> -p <net prototxt> -o <output file> -b ACT -t BOARD_BIN 
   caffe2bin.py -w <caffemodel file> -p <net prototxt> -o <output file> -b ACT -t SIMULATION --qmn 9.7 
   caffe2bin.py -w <caffemodel file> -p <net prototxt> -o <output file> -b ACT -t BOARD_BIN --qmn 9.7
