if [ $# -ne 4 ]; then
    echo "Usage#1: ./run.sh <org|dim> <org|bswap> <input_name> <weight.pickle>"
    exit
fi
if ! ([[ $1 == "org" ]] || [[ $1 == "dim" ]]); then
    echo "Usage#2: ./run.sh <org|dim> <org|bswap> <input_name> <weight.pickle>"
    exit
fi
if ! ([[ $2 == "org" ]] || [[ $2 == "bswap" ]]); then
    echo "Usage#3: ./run.sh <org|dim> <org|bswap> <input_name> <weight.pickle>"
    exit
fi
KERNEL_DIM_MODE=$1
BIAS_SWAP_MODE=$2
INPUT_NAME=$3
WEIGHTS_PICKLE=$4

SYSTEM=`uname -a`
if [[ $SYSTEM = *"Ubuntu"* ]]; then
    PROJECTS=$HOME/projects
else
    PROJECTS=$HOME/Projects
fi

TELLO_YOLO_HOME=$PROJECTS/tello.yolo.code
FRAC_BITS_HOME=$TELLO_YOLO_HOME/frac_bits_json
if [[ $BIAS_SWAP_MODE == "org" ]]; then
	FRAC_BITS_PATH=$FRAC_BITS_HOME/"$INPUT_NAME"_org_frac_bits.json
else
	FRAC_BITS_PATH=$FRAC_BITS_HOME/"$INPUT_NAME"_bswap_frac_bits.json
fi
DNN_FPGA=$TELLO_YOLO_HOME/dnn.fpga

NEW_PYTHONPATH=$PYTHONPATH:$DNN_FPGA/fraqnn.sim
PYTHONPATH=$NEW_PYTHONPATH python fp32tofxp16.py $BIAS_SWAP_MODE $INPUT_NAME $WEIGHTS_PICKLE $FRAC_BITS_PATH index_map.json
#if [[ "$KERNEL_DIM_MODE" == "dim" ]]; then
#	python3 modify_dim.py fxp16-bswap-$WEIGHTS_PICKLE 4
#fi
