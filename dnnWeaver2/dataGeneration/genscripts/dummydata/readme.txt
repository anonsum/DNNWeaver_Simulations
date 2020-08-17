////////////////////////////////////////////////////////////
//// Dummy data generation script for NxM Systolic array 
////////////////////////////////////////////////////////////

 - Creates dummy image and weight data for NXM systolic array 
 - Refere example section for creating data for a lenet type graph 

/////////////////////////////////////////////////////////////

Image :
./genDummyImageData.py -h
usage: genDummyImageData.py [-h] [-m ROW] [-n COL] [-iw WIDTH] [-ih HEIGHT] [-ic IP_CHANNELS] [-fill FILLER]
                            [-stval STARTVALUE] [-out OUT_FILE]
 
optional arguments:
  -h, --help            show this help message and exit
  -m ROW, --row ROW     Systolic array rows (default: 4)
  -n COL, --col COL     Systolic array columns (default: 4)
  -iw WIDTH, --width WIDTH
                        Image width (default: 32)
  -ih HEIGHT, --height HEIGHT
                        Image height (default: 32)
  -ic IP_CHANNELS, --ip_channels IP_CHANNELS
                        Number of output channels (default: 1)
  -fill FILLER, --filler FILLER
                        Weight matrix filler type(const|inc|rand) (default: inc)
  -stval STARTVALUE, --startvalue STARTVALUE
                        Specify the const or start value for inc (default: 1)
  -out OUT_FILE, --out_file OUT_FILE
                        Output file name (default: input_image.txt)

run command : ./genDummyImageData.py -iw 8 -ih 8 -ic 5 -fill inc -stval 100 -out a.txt >& out.log
  
Dummy_weights:
./genDummyWtData.py -h
usage: genDummyWtData.py [-h] [-m ROW] [-n COL] [-oc OP_CHANNELS] [-ic IP_CHANNELS] [-k KERNEL] [-f FILLER]
                         [-of OUT_FILE]
 
optional arguments:
  -h, --help            show this help message and exit
  -m ROW, --row ROW     Systolic array rows (default: 4)
  -n COL, --col COL     Systolic array columns (default: 4)
  -oc OP_CHANNELS, --op_channels OP_CHANNELS
                        Number of output channels (default: 1)
  -ic IP_CHANNELS, --ip_channels IP_CHANNELS
                        Number of output channels (default: 1)
  -k KERNEL, --kernel KERNEL
                        Kernel size (default: 5)
  -f FILLER, --filler FILLER
                        Weight matrix filler type(mod/inc/rand) (default: inc_all)
  -stval STARTVALUE, --startvalue STARTVALUE
                         Specify the const or start value for inc (default: 1)
  -of OUT_FILE, --out_file OUT_FILE
                        Output file name (default: dummy_weights.txt)
 
Note: This script is only for NxM = 4x4 systolic array. 

Example : 
   In dnnweaver2_lenet, Qmn is 9.7 , select stval such that multiplication 
   of dummy image pixel x weight pixel should have valid data from 7th bit.

path:svn/FPGACNNProject/dnnWeaver2/dnnweaver2_lenet/simulation/data

Graph Nodes: conv0/maxpool1,
             input image = [batch_size,8,8,4] //IC for input image should be <= 4  
             weights_conv0 = [10,3,3,4]
             bias = 10

	     conv1/maxpool2,
	     weights_conv1 = [6,3,3,10]
             bias = 6

	     FC0,
	     weights_fc0 = [12,3,3,6]
	     bias = 12

	     FC1,
	     weights_fc1 = [10,3,3,12]
	     bias = 10

Dummy image_data:

./genDummyImageData.py -iw 8 -ih 8 -ic 4 -out img.hex >& img.log

After generating dummy image_data, copy <file>.hex (i.e img.hex- image in hex format)  to simulation/data/inputimage.txt

Dummy Weight_data:

Note: set stval for all dummy weight_data layers, because weight data will control Qmn at all layers.

 For 8x8 image , 3x3 kernel,
 Layer1 : conv0+maxpool1

 set layer1 IC to 4 ,same as in dummy image_data IC    

 ./genDummyWtData.py -ic 4 -oc 10 -k 3 -stval 400 -of w_conv0 >& w_conv0.log

 copy w_conv0.dec_hex to simulation/data/whex_conv0.txt

 Layer2 : conv1+maxpool2
 Here, layer1 OC will be layer2 IC , so set IC to 10 in layer2. 

 ./genDummyWtData.py -ic 10 -oc 6 -k 3 -stval 500 -of w_conv1 >& w_conv1.log

 similarly, copy w_conv1.dec_hex to simulation/data/whex_conv1.txt 
     	   
 Layer3 : FC0
 Here, layer2 OC will be layer3 IC, so set IC to 6 in layer3.

 ./genDummyWtData.py -ic 6 -oc 12 -k 3 -stval 600 -of w_fc0 >& w_fc0.log
 
 similarly, copy w_fc0.dec_hex to simulation/data/whex_fc0.txt

 Layer4 : FC1
 Here, each input of FC1 is considered as one input channel (flattened 1D),
 interchange ic and oc for fc1 layer. so set OC to 12 ( i.e. 12 is IC for fc1 )

 ./genDummyWtData.py -ic 10 -oc 12 -k 3 -stval 700 -of w_fc1 >& w_fc1.log

 similarly, copy w_fc1.dec_hex to simulation/data/whex_fc1.txt
