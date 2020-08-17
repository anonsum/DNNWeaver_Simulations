
#### Sample Script to create Lenet classifer .bin files for simulation and board 

#### Usage : ./createdata_lenet.sh  		: to generate board_data and sim_data folders 
#### 	     ./createdata_lenet.sh cleanall  	: to delete the data files and log. 

CreateData()
{
	echo "Creating SIMULATION data..."
	echo "Creating weights data..."
	rm -rf sim_data
	mkdir -p sim_data
	../dataconverters/src/caffe2bin.py  -w ../prototxt/lenet/lenet_snapshot_20conv_50conv_500ip1_iter_10000.caffemodel -p ../prototxt/lenet/lenet.prototxt -o sim_data/SIM_WT_Q9_7_20ch_50ch_500ip1.txt -b ACT -t SIMULATION >& sim_data/sim_wt.log
	echo "Creating input image data..."
	mkdir sim_data/test_images
	for i in {0..9}
	do
		../dataconverters/src/genImageData.py  -i ../images/mnist_images/${i}_img.bmp -o sim_data/test_images/${i}_img.txt -t SIMULATION 
	done >& sim_data/sim_img_data.log
	
	
	echo "Creating BOARD data..."
	echo "Creating weights data..."
	rm -rf board_data
	mkdir -p board_data
	../dataconverters/src/caffe2bin.py -w ../prototxt/lenet/lenet_snapshot_20conv_50conv_500ip1_iter_10000.caffemodel -p ../prototxt/lenet/lenet.prototxt -o board_data/BOARD_WT_Q9_7_20ch_50ch_500ip1.bin -b ACT -t BOARD_BIN >& ./board_data/board_wt.log
	echo "Creating input image data..."
	mkdir board_data/test_images
	for i in {0..9}
	do
		../dataconverters/src/genImageData.py -i ../images/mnist_images/${i}_img.bmp -o board_data/test_images/${i}_img.bin -t BOARD_BIN 
	done >& ./board_data/board_img_data.log


	rm -f temp.txt 
}


if [ $1 ]
then
	if [ $1 == "clean" ]
	then
		rm -f ./sim_data/*.log *.txt
		rm -f ./board_data/*.log ./board_data/*.txt 
	fi
	if [ $1 == "cleanall" ]
	then
		rm -rf *.log *.txt sim_data board_data
	fi	
else
	source ./rccaffe 	## set caffe installation path  
	CreateData
fi	
