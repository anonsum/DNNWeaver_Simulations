### script to generate weightimagehex_in.txt file ( for simulation DDR loading) _

var_weight="nn_weights.txt"  
var_image="image_hex.txt"
var_simdata="weightimghex_in.txt" # do not change 

### LeNet prototxt Weights 
source ../../../software/scripts/rccaffe 
../../../software/dataconverters/src/caffe2bin.py -w ../../../software/prototxt/lenet/lenet_snapshot_20conv_50conv_500ip1_iter_10000.caffemodel -p ../../../software/prototxt/lenet/lenet.prototxt  -o $var_weight  -b ACT -t SIMULATION --qmn 9.7
### Lenet test image 
../../../software/dataconverters/src/genImageData.py -i ../../../software/images/mnist_images/0_img.bmp -o $var_image -t SIMULATION --qmn 9.7

### cancat 
cat $var_weight > $var_simdata  
cat $var_image >> $var_simdata  

### 
rm -rf $var_weight $var_image 
rm -rf temp.txt 

