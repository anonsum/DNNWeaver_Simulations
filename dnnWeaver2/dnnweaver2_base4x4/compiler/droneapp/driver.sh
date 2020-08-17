#/bin/bash

if [ $# -lt 4 ]; then
	echo "Usage: ./driver.sh <drone|webcam|videofile> <tf-cpu|tf-gpu|dnnweaver2> <tf-weight.pickle> <dnnweaver2-wegiht.pickle> [<input videofile>] [<output videofile>]"
	exit
fi

CAM_SRC=$1
YOLO_ENGINE=$2
TF_WEIGHT_PICKLE=$3
DW2_WEIGHT_PICKLE=$4
if [[ "$CAM_SRC" = *"webcam"* ]]; then
	rmmod uvcvideo
	modprobe uvcvideo nodrop=1 timeout=10000 quirks=0x80
	INVIDEOFILE=
	OUTVIDEOFILE=
elif [[ "$CAM_SRC" = *"videofile"* ]]; then 
	INVIDEOFILE=$5
	OUTVIDEOFILE=$6
fi

PYTHONPATH=.. python driver.py $CAM_SRC $YOLO_ENGINE $TF_WEIGHT_PICKLE $DW2_WEIGHT_PICKLE $INVIDEOFILE $OUTVIDEOFILE
#PYTHONPATH=../dnnweaver2 python driver.py $CAM_SRC $YOLO_ENGINE $TF_WEIGHT_PICKLE $DW2_WEIGHT_PICKLE $INVIDEOFILE $OUTVIDEOFILE
#PYTHONPATH=../compiler python driver.py $CAM_SRC $YOLO_ENGINE $TF_WEIGHT_PICKLE $DW2_WEIGHT_PICKLE $INVIDEOFILE $OUTVIDEOFILE

