A. This is the baseline dnnWeaver2 for tiny yolo2 simulation.

B. Systolic array size:
    array_m = 8
    array_n = 8

C. Few changes in the compiler:
    1. Address space has been reduced to make it possible to simulate
       using iverilog.
       compiler/dnnweaver2/compiler/__init__.py
       line 52 commented out and line 55 used
    
    2. Hardcoded extra padding space added.
       compiler/dnnweaver2/tensor.py
       line 54 to line 59 added to extra 3x3 padding space

    3. Reverted back a small change in pu_compiler.py
       line 152 and 153 uncommented. Line 154 and 155
       commented out.

D. To compile:
    a. cd compiler
    b. source ../env/rctensorflow
    c. python yolo2_demo.py
       [Note: yolo2_demo.py : contains top level calls
              yolo2_tiny.py : contains the tiny yolo2 graph] 

E. For more detailed information on data preparation
   refer to data/readme.txt

F. In simulation/tb/axi_master_tb_driver.v, following data, weights, bias, 
   mean, scale, output addresses need to be updated from the compiler log.
   Sample logging is as follows,

    INFO:Graph Compiler:MS : Addr -- Data : 0x0 	 Weights : 0x2b5000
    INFO:Graph Compiler:MS : Addr -- Bias : 0x2b7c00 	 Outputs : 0x2b8800 	 Elements : (1, 416, 416, 16)
    INFO:PU Compiler:SS : In Layer :conv0/batch_norm/BatchNorm
    INFO:PU Compiler:SS : Addr -- Mean : 0x1d83c00
    INFO:PU Compiler:SS : Addr -- Scale : 0x1d84800

G. simulation/tb/axi_master_tb_driver.v ddr_ram size is changed to 
   reg [15:0] ddr_ram [0:(1<<27)-1]; // Basically ddr_ram is 16 bit now

