
##### Dependencies and pretrained models and weights 

Real time object detection with tiny-yolo model

	* tiny-yolo has an efficient approach as it first predicts which parts of the image contains required information and then runs the classifiers on these parts only. 
	* Simply put, tiny-yolo divides up the images into a grid of 13 by 13 cells which are further divided into 5 “bounding boxes”. 
	* A bounding box is a rectangle that encloses an object. For each bounding box, it parallel runs a recognition algorithm to identify which image class do they belong to. 
	* tiny-yolo eventually outputs a confidence (probability) score that tells us how certain it is that the predicted bounding boxes actually encloses an object (image class). 
	* Each input image is very fast taken thru this special CNN and results with a matrix of (13 x 13 x 125) where each tensor carries unique information like x,y parameters, width/length of bounding box rectangle, confidence score and probability dist over the trained classes of images.
    * Results of the predicted object with bounding box are written to the output using openCV2 library api's


Instructions

1. Clone DnnWeaver2 repository

2. Follow the instructions on the DnnWeaver2 and set up the accelerator on the FPGA board

#####  Run command 

3. Run the driver.py with the dnnweaver2 directory included on the PYTHONPATH

	* Drone+DnnWeaver:  ./driver.sh drone dnnweaver2 weights/yolo2_tiny_tf_weights.pickle weights/yolo2_tiny_dnnweaver2_weights.pickle
	* Videofile+TF-CPU: ./driver.sh videofile tf-cpu weights/yolo2_tiny_tf_weights.pickle weights/yolo2_tiny_dnnweaver2_weights.pickle videofiles/video.mp4 videofiles/video-out.mp4

4. Enter 'e' to stop execution

##### Run scripts for VideoFile+ TFCPU 
  > source ../../env/.rctensorflow   ( setup tensorflow env) 
  > ./run.sh >& run.log 
  > e   				( enter e to stop execution) 


##### inputs 
 input  : videofiles/video.mp4
 output : videofiles/video_out.mp4  

