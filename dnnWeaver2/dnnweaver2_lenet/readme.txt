//-------------------------------------------------------------------------------
		DNNWeaver2 Compiler and Systolic Array based  Accelerator 

								28-Feb-2020
//--------------------------------------------------------------------------------

Target Configuration Settings:

Systolic Array      : 4x4

Model 		    : Lenet  20-5-500-10 

Input Image         : 28x28 MNIST dataset 

Layers		    : Conv0+Pool0-> Conv1+Pool1-> FC0->FC1

Final FC  Layer o/p : 10 Neurons

//----------------------------------------------------------------------------------

Run Steps: 

Step1: Set Tensor Flow paths & env variables
	 $> source evn/.rctensorflow

	cdnserv2> source env/.rctensorflow 
	(tfpy36cpuenv) cdnserv2> 


Step2 : Generate Instructions
	1) cd compiler
        2) lenet model is specified in "lenet_20_50_500_100_sys4x4.py" file
	3) run compiler -> ./run.sh 

	This Generates the instructions for the network specified in "lenet_20_50_500_100_sys4x4.py". 
	
	4) outputs: 
		- instruction.bin   ( in hex format) 
	        - compiler.log      (contains logs and ddr address for each layer ) 


step3 : Train Lenet (or) Use the pre trained model weights to generate formatted weight data for DDR memory (simulation / board). 
        Use the dataset images to generate the formatted image to be loaded to DDR memory (simulation/board) 

Step4 : Execute Simulation

	1) copy instruction.bin & compiler.log from "compiler" folder to simulation folder

        2) cd simulation

        3) In rtl/rtl/dnnweaver2_controller.v ensure that (ARRAY_M,ARRAY_N)= (num_rows,num_cols) as in graph. 
	
	.py: 
	num_rows = 4
	num_cols = 4

	.v: 
	module dnnweaver2_controller #(
	    parameter integer  NUM_TAGS                     = 2,
	    parameter integer  ADDR_WIDTH                   = 42,
	    parameter integer  ARRAY_N                      = 4,
	    parameter integer  ARRAY_M                      = 4,


        4) Open tb/axi_master_tb_driver.v
	- Open compiler.log & search for string "Addr --"
	- For each Layer there will be entry for Addr (Data,Weight,Bias & output). For eg.      

                    INFO:Graph Compiler:MS : In Layer :fc1/Convolution
                    INFO:Graph Compiler:MS : Addr -- Data : 0xf000 	 Weights : 0x10000
                    INFO:Graph Compiler:MS : Addr -- Bias : 0x11000 	 Outputs : 0x12000

	- line 202 in "tb/axi_master_tb_driver.v" file update these address locations into the paramaters.
	 (from run.log file )

	5) Copy the image and weight generated to data folder. 	

	6 )Now execute simulation ./sim.sh 
  	This runs the iverilog simulaion with the below entries. 
		> iverilog  -c filelist.tb -g2012  -o compiler.out -Dsimulation -I .  -s tb_dnnw2_ctrl


  	8) Output :
		- sim.log
		- tb_dnnw2_ctrl.vcd   ( vcd sump) 

	9) Open gtkwave. The fc_layer.gtkw contains the basic signal of interest. 
   	   gtkwave tb_dnnw2_ctrl.vcd fc_layer.gtkw &


Step 5: Validation 

	Manual Validation 
	
	The example image checked-in for classification is digit 6.  The classified output details are available in sim.log 

	
	FC2 Final Output

	ddr_ram[          0]=               64750 000000000000fcee	
	
	ddr_ram[          1]=               65496 000000000000ffd8
	
	ddr_ram[          2]=               65084 000000000000fe3c
	
	ddr_ram[          3]=                 309 0000000000000135

	ddr_ram[          4]=               65463 000000000000ffb7
	
	ddr_ram[          5]=                 842 000000000000034a
	
	ddr_ram[          6]=                1334 0000000000000536		<< highest value neuron>> - classfied digit = 6 

	ddr_ram[          7]=               64702 000000000000fcbe

	ddr_ram[          8]=                 450 00000000000001c2

	ddr_ram[          9]=               64662 000000000000fc96

	ddr_ram[         10]=                   0 0000000000000000

	ddr_ram[         11]=                   0 0000000000000000


Step 5 : Board Implementation: 
	N/A 


Fixes/Hardcoding : 
-----------------
- Compiler:
 1) complier/dnnweaver2/compiler/__init.py
	- Random seed for address generation removed in alloc() fn : Line 62
	- New alloc_MS() fn defined to ensure that FC layer input takes same address as conv1+pool1 o/p :  Line 41-54
        - _alloc_tensor() fn modified to supports FC layer : Lines 136-142
 2) complier/dnnweaver2/compiler/pu_compiler.py 
        - Ignored pad_offset addition to PoolLayer start addr : Line 149-152.
		- The original code(commented@ line 149-150) was causing issue when conv2 reading input from Pool2 out address.
                - Need to figure out why needed,
                - Commenting lines 149-150 and adding 151-152 fixed the issue for this testcase.
  a) Changed the dumped instructions file from "test.bin" to "instruction.bin"
