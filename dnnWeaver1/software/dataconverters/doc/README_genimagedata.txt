############################################################
genImageData.py : Converts input image data to bin/hex format.
############################################################

usage: genImageData.py [-h] -i INFILE -o OUTFILE [-t TYPE] [-q QMN]

optional arguments:
  -h, --help            		show this help message and exit
  -i INFILE, --infile INFILE 	Input file
  -o OUTFILE, --outfile OUTFILE Output file
  -t TYPE, --type TYPE  		Output type(SIMULATION/BOARD_HEX/BOARD_BIN (default SIMULATION))
  -q QMN, --qmn QMN     		Convert to Qm.n (Default Q9.7)(NO : if not required)


Example:
	genImageData.py -i <input.bmp> -o <output.bmp> -t SIMULATION
	genImageData.py -i <input.bmp> -o <output.bmp> -t BOARD_BIN
	genImageData.py -i <input.bmp> -o <output.bmp> -t SIMULATION --qmn 9.7
	genImageData.py -i <input.bmp> -o <output.bmp> -t BOARD_BIN --qmn 9.7


