//-------------------------------------------------------------------------------
First Working version of DNNWeaver2 Compiler and Systolic Array based  Accelerator 
//--------------------------------------------------------------------------------
									17-07-2019 

Target Configuration Settings:

Systolic Array      : 4x4

Input Image         : 8x8 (R,G,B)

Layers		    : Conv0+Pool0-> Conv1+Pool1-> FC0->FC1

Final FC1 Layer o/p : 2 Neurons

//----------------------------------------------------------------------------------

Major Changes: 
  Removed PCI data path and using direct DDR loading 

//----------------------------------------------------------------------------------

Run Steps: 

Step1: Set Tensor Flow paths & env variables
	 $> source evn/.rctensorflow

	cdnserv2> source env/.rctensorflow 
	(tfpy36cpuenv) cdnserv2> 


Step2 : Generate Instructions
	1) cd compiler
	2) dnnw2_2conv_2fc_arr4x4.py is the demo network graph.  
	3) ./run.sh >& run.log   
	Generate the instructions for graph specified in "dnnw2_2conv_2fc_arr4x4.py". 

	(tfpy36cpuenv) cdnserv2> ./run.sh > run.log 
	INFO:Graph Compiler:MS : In Layer :conv0/Convolution
	INFO:Graph Compiler:MS : Addr -- Data : 0x0 	 Weights : 0x1000
	INFO:Graph Compiler:MS : Addr -- Bias : 0x2000 	 Outputs : 0x3000
	INFO:Graph Compiler:MS : In Layer :conv1/Convolution
	INFO:Graph Compiler:MS : Addr -- Data : 0x6000 	 Weights : 0x7000
	INFO:Graph Compiler:MS : Addr -- Bias : 0x8000 	 Outputs : 0x9000
	INFO:Graph Compiler:MS : In Layer :fc0/Convolution
	INFO:Graph Compiler:MS : Addr -- Data : 0xb000 	 Weights : 0xc000
	INFO:Graph Compiler:MS : Addr -- Bias : 0xd000 	 Outputs : 0xe000
	INFO:Graph Compiler:MS : In Layer :fc1/Convolution
	INFO:Graph Compiler:MS : Addr -- Data : 0xf000 	 Weights : 0x10000
	INFO:Graph Compiler:MS : Addr -- Bias : 0x11000 	 Outputs : 0x12000

        4) Outputs:
		- instruction.bin      -- output instructions in hex format
        	- run.log              -- Contains Address Map for Img& weight data for each layer



Step3 : Execute Simulation

	1) copy instruction.bin & run.log from "compiler" folder to simulation folder

        2) cd simulation

        3) In rtl/rtl/dnnweaver2_controller.v ensure that (ARRAY_M,ARRAY_N)= (num_rows,num_cols) in compiler/dnnw2_2conv_2fc_arr4x4.py
	
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
	- Open run.log & search for string "Addr --"
	- For each Layer there will be entry for Addr (Data,Weight,Bias & output). For eg.      

                    INFO:Graph Compiler:MS : In Layer :fc1/Convolution
                    INFO:Graph Compiler:MS : Addr -- Data : 0xf000 	 Weights : 0x10000
                    INFO:Graph Compiler:MS : Addr -- Bias : 0x11000 	 Outputs : 0x12000

	- line 202 in "tb/axi_master_tb_driver.v" file update these address locations into the paramaters.
	 (from run.log file )

	5) The Image Size and Weight size are calculated based on the zero padding and data arrangements	
	 (Reference : Add reference here) 

        6) The Image and weights data files are kept in "data" folder. The data files are manually prepared for           8x8 image and 4x4 systolic array . Refer documents for data preparating steps. 

	7)Now execute simulation ./sim.sh 
 	This runs the iverilog simulaion with the below entries. 
		> iverilog  -c filelist.tb -g2012  -o compiler.out -Dsimulation -I .  -s tb_dnnw2_ctrl


  	8) Output :
		- sim.log
		- tb_dnnw2_ctrl.vcd   ( vcd sump) 

	9) Open gtkwave. The fc_layer.gtkw contains the basic signal of interest. 
   	   gtkwave tb_dnnw2_ctrl.vcd fc_layer.gtkw &


Step 4: Validation 

	Manual Validation 



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
  3) Changed the dumped instructions file from "test.bin" to "instruction.bin"

-simulation :
 1) In rtl/mxv/instruction_memory_noPCI.v file, replace test.bin with "instruction.bin" in Line 219 


