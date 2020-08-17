//------------------------------------------------------------------------------------
//	  Caffe Training and Data Generation Scripts for Open Source DNNWEAVER2 System  
//------------------------------------------------------------------------------------
//------------------------------------------------------------------------------------
// 									 05-March-2020 
//-------------------------------------------------------------------------------------

I. Requirements 
        1. caffe installation
        2. python 2.7

II. Directory Structure   
    dataGeneration|	
		  |-- caffemodelzoo	(trained caffemodels)
		  |-- dataset		(dataset for training and testing caffe models) 
		  |-- trainmodel	(scripts  to train model) 
		  |-- env		(caffe env setup)
		  |-- genscripts	(scripts to generate files for DW2 simulation and boards)
		  |-- prototxt		(caffe prototxt for training and testing)

III. Training of LeNet Model(optional): 
     This section explains the training steps. The trained caffemodels are available at caffemodelzoo. 
       > source env/rccaffe 
       > cd trainmodel 
       > ./train_lenet.py

     This use the prototxt/lenet model for caffe training  and generate the results at caffemodelzoo/lenet/*  	

     // training log
	I0305 16:59:10.080751 11114 solver.cpp:464] Snapshotting to binary proto file ../caffemodelzoo/lenet/snapshot_20ch_50ch_500ch_10ch_lenet_iter_10000.caffemodel
	I0305 16:59:10.098346 11114 sgd_solver.cpp:284] Snapshotting solver state to binary proto file ../caffemodelzoo/lenet/snapshot_20ch_50ch_500ch_10ch_lenet_iter_10000.solverstate
	I0305 16:59:10.118186 11114 solver.cpp:327] Iteration 10000, loss = 0.0102166
	I0305 16:59:10.118214 11114 solver.cpp:347] Iteration 10000, Testing net (#0)
	I0305 16:59:12.585337 11116 data_layer.cpp:73] Restarting data prefetching from start.
	I0305 16:59:12.687661 11114 solver.cpp:414]     Test net output #0: accuracy = 0.9857
	I0305 16:59:12.687693 11114 solver.cpp:414]     Test net output #1: loss = 0.0447749 (* 1 = 0.0447749 loss)
	I0305 16:59:12.687702 11114 solver.cpp:332] Optimization Done.
	I0305 16:59:12.687708 11114 caffe.cpp:250] Optimization Done. 


IV. DataGeneration: 
    The image data and trained weights need to formatted for DW2 simulation. 
    > cd genscripts 
	run the run.sh scripts in the following directories to generate data. 
	all the data are in q9.7 format. 
	    image_input_prep			-- generate input image data in hex format  
	    weight_prep				-- generate weights for all the layers in prototxt 
	    lenet_layerresults_compute		-- generate computed data output of each layer for manual verification. 
    	

V. Copy files to Lenet simulation folder.      	
	copy the generate image and weight files to  dnnweaver2_lenet/simulation/data/
	The file names should be as below. 
		inputimage.txt  whex_conv0.txt  whex_conv1.txt  whex_fc0.txt  whex_fc1.txt	

VI. cd to dnnweaver2_lenet/simulation/ and run the simulations. 

