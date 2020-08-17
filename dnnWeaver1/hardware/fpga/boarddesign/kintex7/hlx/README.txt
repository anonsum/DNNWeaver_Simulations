Requirements:
-  Vivado Version 2015.4
-  gensys2 Kintex board


Steps to Execute
1) Create Vivado project 
    a) Launch Vivado
    b) source dnn.tcl  
    c) The Vivado project and hierarchy will be created for Microblaze based system
    d) Generate Bitstream
    e) File->Export->Export Hardware (Tick include bitstream checkbox)   : Will export the hardware to SDK

2) Launch SDK and program board
   a) SDK can be launched standalone or through Vivado Project (File->Launch SDK)
   b) A sample SDK project is present in "sw" folder. It can be used as is
   c) If creating a fresh SDK project
         - Create a new "Hello world" standalone application
         - Copy the helloworld.c file from sw->dnn folder into 
         - Connect the board JTAG and USB cables to PC
         - XilinxTool->Program FPGA : will program the FPGA with bitstream+bootload file
         - Configure TeraTerm for baud rate 115200.
         - In XMD console
             - connect mb mdm
             - rst;stop
             - dow <elf file>; run
         - Through TeraTerm load the weight file followed by Image file (Binary) 


