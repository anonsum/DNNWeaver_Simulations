`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 04/03/2019 09:17:45 AM
// Design Name: 
// Module Name: tb_dnnw2_ctrl
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////


module tb_dnnw2_ctrl(

    );

    parameter integer  NUM_TAGS                     = 2;
    parameter integer  ADDR_WIDTH                   = 42;
    parameter integer  ARRAY_N                      = 2;
    parameter integer  ARRAY_M                      = 2;

  // Precision
    parameter integer  DATA_WIDTH                   = 16;
    parameter integer  BIAS_WIDTH                   = 32;
    parameter integer  ACC_WIDTH                    = 64;

  // Buffers
    parameter integer  IBUF_CAPACITY_BITS           = ARRAY_N * DATA_WIDTH * 2048;
    parameter integer  WBUF_CAPACITY_BITS           = ARRAY_N * ARRAY_M * DATA_WIDTH * 512;
    parameter integer  OBUF_CAPACITY_BITS           = ARRAY_M * ACC_WIDTH * 2048;
    parameter integer  BBUF_CAPACITY_BITS           = ARRAY_M * BIAS_WIDTH * 2048;

  // Buffer Addr Width
    parameter integer  IBUF_ADDR_WIDTH              = $clog2(IBUF_CAPACITY_BITS / ARRAY_N / DATA_WIDTH);
    parameter integer  WBUF_ADDR_WIDTH              = $clog2(WBUF_CAPACITY_BITS / ARRAY_N / ARRAY_M / DATA_WIDTH);
    parameter integer  OBUF_ADDR_WIDTH              = $clog2(OBUF_CAPACITY_BITS / ARRAY_M / ACC_WIDTH);
    parameter integer  BBUF_ADDR_WIDTH              = $clog2(BBUF_CAPACITY_BITS / ARRAY_M / BIAS_WIDTH);

  // Instructions
    parameter integer  INST_ADDR_WIDTH              = 32;
    parameter integer  INST_DATA_WIDTH              = 32;
    parameter integer  INST_WSTRB_WIDTH             = INST_DATA_WIDTH / 8;
    parameter integer  INST_BURST_WIDTH             = 8;
    parameter integer  LOOP_ITER_W                  = 16;
    parameter integer  ADDR_STRIDE_W                = 32;
    parameter integer  MEM_REQ_W                    = 16;
    parameter integer  BUF_TYPE_W                   = 2;
    parameter integer  LOOP_ID_W                    = 5;
  // AGU
    parameter integer  OFFSET_W                     = ADDR_WIDTH;
  // AXI
    parameter integer  AXI_ADDR_WIDTH               = 42;
    parameter integer  AXI_ID_WIDTH                 = 1;
    parameter integer  AXI_BURST_WIDTH              = 8;
    parameter integer  TID_WIDTH                    = 4;
    parameter integer  IBUF_AXI_DATA_WIDTH          = 64;
    parameter integer  IBUF_WSTRB_W                 = IBUF_AXI_DATA_WIDTH/8;
    parameter integer  WBUF_AXI_DATA_WIDTH          = 64;
    parameter integer  WBUF_WSTRB_W                 = WBUF_AXI_DATA_WIDTH/8;
    parameter integer  OBUF_AXI_DATA_WIDTH          = 256;
    parameter integer  OBUF_WSTRB_W                 = OBUF_AXI_DATA_WIDTH/8;
    parameter integer  PU_AXI_DATA_WIDTH            = 64;
    parameter integer  PU_WSTRB_W                   = PU_AXI_DATA_WIDTH/8;
    parameter integer  BBUF_AXI_DATA_WIDTH          = 64;
    parameter integer  BBUF_WSTRB_W                 = BBUF_AXI_DATA_WIDTH/8;
  // AXI-Lite
    parameter integer  CTRL_ADDR_WIDTH              = 32;
    parameter integer  CTRL_DATA_WIDTH              = 32;
    parameter integer  CTRL_WSTRB_WIDTH             = CTRL_DATA_WIDTH/8;
  // Instruction Mem
    parameter integer  IMEM_ADDR_W                  = 7;
  // Systolic Array
    parameter integer  TAG_W                        = $clog2(NUM_TAGS);
    parameter          DTYPE                        = "FXP"; // FXP for dnnweaver2; FP32 for single precision; FP16 for half-precision
    parameter integer  WBUF_DATA_WIDTH              = ARRAY_N * ARRAY_M * DATA_WIDTH;
    parameter integer  BBUF_DATA_WIDTH              = ARRAY_M * BIAS_WIDTH;
    parameter integer  IBUF_DATA_WIDTH              = ARRAY_N * DATA_WIDTH;
    parameter integer  OBUF_DATA_WIDTH              = ARRAY_M * ACC_WIDTH;

  // Buffer Addr width for PU access to OBUF
    parameter integer  PU_OBUF_ADDR_WIDTH           = OBUF_ADDR_WIDTH + $clog2(OBUF_DATA_WIDTH / OBUF_AXI_DATA_WIDTH);

    reg                                         clk;
    reg                                         reset;
    reg                                         start;
    reg [12     -1 : 0 ]                        num_blocks_in;


  // Slave Write address
    reg                                         pci_cl_ctrl_awvalid;
    reg  [ CTRL_ADDR_WIDTH      -1 : 0 ]        pci_cl_ctrl_awaddr;
    wire                                         pci_cl_ctrl_awready;
  // Slave Write data
    reg                                         pci_cl_ctrl_wvalid;
    reg  [ CTRL_DATA_WIDTH      -1 : 0 ]        pci_cl_ctrl_wdata;
    reg  [ CTRL_WSTRB_WIDTH     -1 : 0 ]        pci_cl_ctrl_wstrb;
    wire                                         pci_cl_ctrl_wready;
  // Slave Write response
    wire                                         pci_cl_ctrl_bvalid;
    wire  [ 2                    -1 : 0 ]        pci_cl_ctrl_bresp;
    reg                                         pci_cl_ctrl_bready;
  // Slave Read address
    reg                                         pci_cl_ctrl_arvalid;
    reg  [ CTRL_ADDR_WIDTH      -1 : 0 ]        pci_cl_ctrl_araddr;
    wire                                         pci_cl_ctrl_arready;
  // Slave Read data/response
    wire                                         pci_cl_ctrl_rvalid;
    wire  [ CTRL_DATA_WIDTH      -1 : 0 ]        pci_cl_ctrl_rdata;
    wire  [ 2                    -1 : 0 ]        pci_cl_ctrl_rresp;
    reg                                         pci_cl_ctrl_rready;

  // PCIe -> CL_wrapper AXI4 interface
  // Slave Interface Write Address
    reg   [ INST_ADDR_WIDTH      -1 : 0 ]        pci_cl_data_awaddr;
    reg   [ INST_BURST_WIDTH     -1 : 0 ]        pci_cl_data_awlen;
    reg   [ 3                    -1 : 0 ]        pci_cl_data_awsize;
    reg   [ 2                    -1 : 0 ]        pci_cl_data_awburst;
    reg                                          pci_cl_data_awvalid;
    wire                                         pci_cl_data_awready;
  // Slave Interface Write Data
    reg   [ INST_DATA_WIDTH      -1 : 0 ]        pci_cl_data_wdata;
    reg   [ INST_WSTRB_WIDTH     -1 : 0 ]        pci_cl_data_wstrb;
    reg                                          pci_cl_data_wlast;
    reg                                          pci_cl_data_wvalid;
    wire                                         pci_cl_data_wready;
  // Slave Interface Write Response
    wire  [ 2                    -1 : 0 ]        pci_cl_data_bresp;
    wire                                         pci_cl_data_bvalid;
    reg                                          pci_cl_data_bready;
  // Slave Interface Read Address
    reg   [ INST_ADDR_WIDTH      -1 : 0 ]        pci_cl_data_araddr;
    reg   [ INST_BURST_WIDTH     -1 : 0 ]        pci_cl_data_arlen;
    reg   [ 3                    -1 : 0 ]        pci_cl_data_arsize;
    reg   [ 2                    -1 : 0 ]        pci_cl_data_arburst;
    reg                                          pci_cl_data_arvalid;
    wire                                         pci_cl_data_arready;
  // Slave Interface Read Data
    wire  [ INST_DATA_WIDTH      -1 : 0 ]        pci_cl_data_rdata;
    wire  [ 2                    -1 : 0 ]        pci_cl_data_rresp;
    wire                                         pci_cl_data_rlast;
    wire                                         pci_cl_data_rvalid;
    reg                                          pci_cl_data_rready;

  // CL_wrapper -> DDR0 AXI4 interface
  // Master Interface Write Address
    wire  [ AXI_ADDR_WIDTH       -1 : 0 ]        cl_ddr0_awaddr;
    wire  [ AXI_BURST_WIDTH      -1 : 0 ]        cl_ddr0_awlen;
    wire  [ 3                    -1 : 0 ]        cl_ddr0_awsize;
    wire  [ 2                    -1 : 0 ]        cl_ddr0_awburst;
    wire                                         cl_ddr0_awvalid;
    wire                                         cl_ddr0_awready;
    //reg                                          cl_ddr0_awready;

  // Master Interface Write Data
    wire  [ IBUF_AXI_DATA_WIDTH  -1 : 0 ]        cl_ddr0_wdata;
    wire  [ IBUF_WSTRB_W         -1 : 0 ]        cl_ddr0_wstrb;
    wire                                         cl_ddr0_wlast;
    wire                                         cl_ddr0_wvalid;
    wire                                         cl_ddr0_wready;
    //reg                                          cl_ddr0_wready;
  // Master Interface Write Response
    wire  [ 2                    -1 : 0 ]        cl_ddr0_bresp;
    wire                                         cl_ddr0_bvalid;
    //reg   [ 2                    -1 : 0 ]        cl_ddr0_bresp;
    //reg                                          cl_ddr0_bvalid;
    wire                                         cl_ddr0_bready;
  // Master Interface Read Address
    wire  [ AXI_ADDR_WIDTH       -1 : 0 ]        cl_ddr0_araddr;
    wire  [ AXI_BURST_WIDTH      -1 : 0 ]        cl_ddr0_arlen;
    wire  [ 3                    -1 : 0 ]        cl_ddr0_arsize;
    wire  [ 2                    -1 : 0 ]        cl_ddr0_arburst;
    wire                                         cl_ddr0_arvalid;
    wire  [ AXI_ID_WIDTH         -1 : 0 ]        cl_ddr0_arid;
    wire                                         cl_ddr0_arready;
    //reg                                          cl_ddr0_arready;
  // Master Interface Read Data
    //reg   [ IBUF_AXI_DATA_WIDTH  -1 : 0 ]        cl_ddr0_rdata;
    //reg   [ AXI_ID_WIDTH         -1 : 0 ]        cl_ddr0_rid;
    //reg   [ 2                    -1 : 0 ]        cl_ddr0_rresp;
    //reg                                          cl_ddr0_rlast;
    //reg                                          cl_ddr0_rvalid;
    wire    [ IBUF_AXI_DATA_WIDTH  -1 : 0 ]      cl_ddr0_rdata;
    wire    [ AXI_ID_WIDTH         -1 : 0 ]      cl_ddr0_rid;
    wire    [ 2                    -1 : 0 ]      cl_ddr0_rresp;
    wire                                         cl_ddr0_rlast;
    wire                                         cl_ddr0_rvalid;
    wire                                         cl_ddr0_rready;

  // CL_wrapper -> DDR1 AXI4 interface
  // Master Interface Write Address
    wire  [ AXI_ADDR_WIDTH       -1 : 0 ]        cl_ddr1_awaddr;
    wire  [ AXI_BURST_WIDTH      -1 : 0 ]        cl_ddr1_awlen;
    wire  [ 3                    -1 : 0 ]        cl_ddr1_awsize;
    wire  [ 2                    -1 : 0 ]        cl_ddr1_awburst;
    wire                                         cl_ddr1_awvalid;
    reg                                          cl_ddr1_awready;
  // Master Interface Write Data
    wire  [ OBUF_AXI_DATA_WIDTH  -1 : 0 ]        cl_ddr1_wdata;
    wire  [ OBUF_WSTRB_W         -1 : 0 ]        cl_ddr1_wstrb;
    wire                                         cl_ddr1_wlast;
    wire                                         cl_ddr1_wvalid;
    reg                                          cl_ddr1_wready;
  // Master Interface Write Response
    reg   [ 2                    -1 : 0 ]        cl_ddr1_bresp;
    reg                                          cl_ddr1_bvalid;
    wire                                         cl_ddr1_bready;
  // Master Interface Read Address
    wire  [ AXI_ADDR_WIDTH       -1 : 0 ]        cl_ddr1_araddr;
    wire  [ AXI_BURST_WIDTH      -1 : 0 ]        cl_ddr1_arlen;
    wire  [ 3                    -1 : 0 ]        cl_ddr1_arsize;
    wire  [ 2                    -1 : 0 ]        cl_ddr1_arburst;
    wire                                         cl_ddr1_arvalid;
    wire  [ AXI_ID_WIDTH         -1 : 0 ]        cl_ddr1_arid;
    reg                                          cl_ddr1_arready;
  // Master Interface Read Data
    reg   [ OBUF_AXI_DATA_WIDTH  -1 : 0 ]        cl_ddr1_rdata;
    reg   [ AXI_ID_WIDTH         -1 : 0 ]        cl_ddr1_rid;
    reg   [ 2                    -1 : 0 ]        cl_ddr1_rresp;
    reg                                          cl_ddr1_rlast;
    reg                                          cl_ddr1_rvalid;
    wire                                         cl_ddr1_rready;

  // CL_wrapper -> DDR2 AXI4 interface
  // Master Interface Write Address
    wire  [ AXI_ADDR_WIDTH       -1 : 0 ]        cl_ddr2_awaddr;
    wire  [ AXI_BURST_WIDTH      -1 : 0 ]        cl_ddr2_awlen;
    wire  [ 3                    -1 : 0 ]        cl_ddr2_awsize;
    wire  [ 2                    -1 : 0 ]        cl_ddr2_awburst;
    wire                                         cl_ddr2_awvalid;
    reg                                          cl_ddr2_awready;
  // Master Interface Write Data
    wire  [ WBUF_AXI_DATA_WIDTH  -1 : 0 ]        cl_ddr2_wdata;
    wire  [ WBUF_WSTRB_W         -1 : 0 ]        cl_ddr2_wstrb;
    wire                                         cl_ddr2_wlast;
    wire                                         cl_ddr2_wvalid;
    reg                                          cl_ddr2_wready;
  // Master Interface Write Response
    reg   [ 2                    -1 : 0 ]        cl_ddr2_bresp;
    reg                                          cl_ddr2_bvalid;
    wire                                         cl_ddr2_bready;
  // Master Interface Read Address
    wire  [ AXI_ADDR_WIDTH       -1 : 0 ]        cl_ddr2_araddr;
    wire  [ AXI_BURST_WIDTH      -1 : 0 ]        cl_ddr2_arlen;
    wire  [ 3                    -1 : 0 ]        cl_ddr2_arsize;
    wire  [ 2                    -1 : 0 ]        cl_ddr2_arburst;
    wire                                         cl_ddr2_arvalid;
    wire  [ AXI_ID_WIDTH         -1 : 0 ]        cl_ddr2_arid;
    reg                                          cl_ddr2_arready;
  // Master Interface Read Data
    reg   [ WBUF_AXI_DATA_WIDTH  -1 : 0 ]        cl_ddr2_rdata;
    reg   [ AXI_ID_WIDTH         -1 : 0 ]        cl_ddr2_rid;
    reg   [ 2                    -1 : 0 ]        cl_ddr2_rresp;
    reg                                          cl_ddr2_rlast;
    reg                                          cl_ddr2_rvalid;
    wire                                         cl_ddr2_rready;

  // CL_wrapper -> DDR3 AXI4 interface
  // Master Interface Write Address
    wire  [ AXI_ADDR_WIDTH       -1 : 0 ]        cl_ddr3_awaddr;
    wire  [ AXI_BURST_WIDTH      -1 : 0 ]        cl_ddr3_awlen;
    wire  [ 3                    -1 : 0 ]        cl_ddr3_awsize;
    wire  [ 2                    -1 : 0 ]        cl_ddr3_awburst;
    wire                                         cl_ddr3_awvalid;
    reg                                           cl_ddr3_awready;
  // Master Interface Write Data
    wire  [ BBUF_AXI_DATA_WIDTH  -1 : 0 ]        cl_ddr3_wdata;
    wire  [ BBUF_WSTRB_W         -1 : 0 ]        cl_ddr3_wstrb;
    wire                                         cl_ddr3_wlast;
    wire                                         cl_ddr3_wvalid;
    reg                                          cl_ddr3_wready;
  // Master Interface Write Response
    reg  [ 2                    -1 : 0 ]        cl_ddr3_bresp;
    reg                                          cl_ddr3_bvalid;
    wire                                         cl_ddr3_bready;
  // Master Interface Read Address
    wire  [ AXI_ADDR_WIDTH       -1 : 0 ]        cl_ddr3_araddr;
    wire  [ AXI_BURST_WIDTH      -1 : 0 ]        cl_ddr3_arlen;
    wire  [ 3                    -1 : 0 ]        cl_ddr3_arsize;
    wire  [ 2                    -1 : 0 ]        cl_ddr3_arburst;
    wire                                         cl_ddr3_arvalid;
    wire  [ AXI_ID_WIDTH         -1 : 0 ]        cl_ddr3_arid;
    reg                                          cl_ddr3_arready;
  // Master Interface Read Data
    reg   [ BBUF_AXI_DATA_WIDTH  -1 : 0 ]        cl_ddr3_rdata;
    reg   [ AXI_ID_WIDTH         -1 : 0 ]        cl_ddr3_rid;
    reg   [ 2                    -1 : 0 ]        cl_ddr3_rresp;
    reg                                          cl_ddr3_rlast;
    reg                                          cl_ddr3_rvalid;
    wire                                         cl_ddr3_rready;

  // CL_wrapper -> DDR3 AXI4 interface
  // Master Interface Write Address
    wire  [ AXI_ADDR_WIDTH       -1 : 0 ]        cl_ddr4_awaddr;
    wire  [ AXI_BURST_WIDTH      -1 : 0 ]        cl_ddr4_awlen;
    wire  [ 3                    -1 : 0 ]        cl_ddr4_awsize;
    wire  [ 2                    -1 : 0 ]        cl_ddr4_awburst;
    wire                                         cl_ddr4_awvalid;
    reg                                          cl_ddr4_awready;
  // Master Interface Write Data
    wire  [ PU_AXI_DATA_WIDTH    -1 : 0 ]        cl_ddr4_wdata;
    wire  [ PU_WSTRB_W           -1 : 0 ]        cl_ddr4_wstrb;
    wire                                         cl_ddr4_wlast;
    wire                                         cl_ddr4_wvalid;
    reg                                          cl_ddr4_wready;
  // Master Interface Write Response
    reg   [ 2                    -1 : 0 ]        cl_ddr4_bresp;
    reg                                          cl_ddr4_bvalid;
    wire                                         cl_ddr4_bready;
  // Master Interface Read Address
    wire  [ AXI_ADDR_WIDTH       -1 : 0 ]        cl_ddr4_araddr;
    wire  [ AXI_BURST_WIDTH      -1 : 0 ]        cl_ddr4_arlen;
    wire  [ 3                    -1 : 0 ]        cl_ddr4_arsize;
    wire  [ 2                    -1 : 0 ]        cl_ddr4_arburst;
    wire                                         cl_ddr4_arvalid;
    wire  [ AXI_ID_WIDTH         -1 : 0 ]        cl_ddr4_arid;
    reg                                          cl_ddr4_arready;
  // Master Interface Read Data
    reg   [ PU_AXI_DATA_WIDTH    -1 : 0 ]        cl_ddr4_rdata;
    reg   [ AXI_ID_WIDTH         -1 : 0 ]        cl_ddr4_rid;
    reg   [ 2                    -1 : 0 ]        cl_ddr4_rresp;
    reg                                          cl_ddr4_rlast;
    reg                                          cl_ddr4_rvalid;
    wire                                         cl_ddr4_rready;

    reg  sel;
    //////////////////////
// IBUF Muxed input Write Address
  wire  [ AXI_ADDR_WIDTH       -1 : 0 ]        ibuf_awaddr;
  wire  [ AXI_BURST_WIDTH      -1 : 0 ]        ibuf_awlen;
  wire  [ 3                    -1 : 0 ]        ibuf_awsize;
  wire  [ 2                    -1 : 0 ]        ibuf_awburst;
  wire                                         ibuf_awvalid;
  wire                                         ibuf_awready;
                                                                  
// Master Interface Write Data
  wire  [ IBUF_AXI_DATA_WIDTH  -1 : 0 ]        ibuf_wdata;
  wire  [ IBUF_WSTRB_W         -1 : 0 ]        ibuf_wstrb;
  wire                                         ibuf_wlast;
  wire                                         ibuf_wvalid;
  wire                                         ibuf_wready;
// Master Interface Write Response
  wire  [ 2                    -1 : 0 ]        ibuf_bresp;
  wire                                         ibuf_bvalid;
  wire                                         ibuf_bready;


assign  ibuf_awaddr  = (sel==1)? cl_ddr0_awaddr  : cl_ddr4_awaddr   ;
assign  ibuf_awlen   = (sel==1)? cl_ddr0_awlen   : cl_ddr4_awlen    ;
assign  ibuf_awsize  = (sel==1)? cl_ddr0_awsize  : cl_ddr4_awsize   ;
assign  ibuf_awburst = (sel==1)? cl_ddr0_awburst : cl_ddr4_awburst  ;
assign  ibuf_awvalid = (sel==1)? cl_ddr0_awvalid : cl_ddr4_awvalid  ;
assign  ibuf_awready = (sel==1)? cl_ddr0_awready : cl_ddr4_awready  ;
assign  ibuf_wdata   = (sel==1)? cl_ddr0_wdata   : cl_ddr4_wdata    ;
assign  ibuf_wstrb   = (sel==1)? cl_ddr0_wstrb   : cl_ddr4_wstrb    ;
assign  ibuf_wlast   = (sel==1)? cl_ddr0_wlast   : cl_ddr4_wlast    ;
assign  ibuf_wvalid  = (sel==1)? cl_ddr0_wvalid  : cl_ddr4_wvalid   ;
assign  ibuf_wready  = (sel==1)? cl_ddr0_wready  : cl_ddr4_wready   ;
assign  ibuf_bresp   = (sel==1)? cl_ddr0_bresp   : cl_ddr4_bresp    ;
assign  ibuf_bvalid  = (sel==1)? cl_ddr0_bvalid  : cl_ddr4_bvalid   ;
assign  ibuf_bready  = (sel==1)? cl_ddr0_bready  : cl_ddr4_bready   ;






    ////////////////////// 
axi_master_tb_driver
#(
    .AXI_DATA_WIDTH           ( IBUF_AXI_DATA_WIDTH                   ),
    .OP_WIDTH                 ( IBUF_AXI_DATA_WIDTH                 ),
    .NUM_PE                   ( 32                   ),
    .BASE_ADDR                (32'h0000_0000             ),
    .TX_SIZE_WIDTH            ( 25            )
) ibuf_axim_driver (
    .clk                      ( clk                      ),
    .reset                    ( reset                    ),     
    .M_AXI_AWID               ( 0               ),   
    .M_AXI_AWADDR             ( ibuf_awaddr  ),   
    .M_AXI_AWLEN              ( ibuf_awlen   ),   
    .M_AXI_AWSIZE             ( ibuf_awsize  ),   
    .M_AXI_AWBURST            ( ibuf_awburst ),   
    .M_AXI_AWLOCK             ( 0               ),   
    .M_AXI_AWCACHE            ( 0               ),   
    .M_AXI_AWPROT             ( 0               ),   
    .M_AXI_AWQOS              ( 0               ),   
    .M_AXI_AWVALID            ( ibuf_awvalid ),   
    .M_AXI_AWREADY            ( ibuf_awready ),   
    .M_AXI_WID                ( 0               ),   
    .M_AXI_WDATA              ( ibuf_wdata   ),   
    .M_AXI_WSTRB              ( ibuf_wstrb   ),   
    .M_AXI_WLAST              ( ibuf_wlast   ),   
    .M_AXI_WVALID             ( ibuf_wvalid  ),   
    .M_AXI_WREADY             ( ibuf_wready  ),   
    .M_AXI_BID                (                 ),   
    .M_AXI_BRESP              ( ibuf_bresp   ),   
    .M_AXI_BVALID             ( ibuf_bvalid  ),   
    .M_AXI_BREADY             ( ibuf_bready  ),   

    .M_AXI_ARID               ( cl_ddr0_rid     ),   
    .M_AXI_ARADDR             ( cl_ddr0_araddr  ),   
    .M_AXI_ARLEN              ( cl_ddr0_arlen   ),   
    .M_AXI_ARSIZE             ( cl_ddr0_arsize  ),   
    .M_AXI_ARBURST            ( cl_ddr0_arburst ),   
    .M_AXI_ARLOCK             ( 0               ),   
    .M_AXI_ARCACHE            ( 0               ),
    .M_AXI_ARPROT             ( 0               ),
    .M_AXI_ARQOS              ( 0               ),
    .M_AXI_ARVALID            ( cl_ddr0_arvalid ),
    .M_AXI_ARREADY            ( cl_ddr0_arready ),
    .M_AXI_RID                ( cl_ddr0_arid    ),
    .M_AXI_RDATA              ( cl_ddr0_rdata   ),
    .M_AXI_RRESP              ( cl_ddr0_rresp   ),
    .M_AXI_RLAST              ( cl_ddr0_rlast   ),
    .M_AXI_RVALID             ( cl_ddr0_rvalid  ),
    .M_AXI_RREADY             ( cl_ddr0_rready  )
);
    
axi_master_tb_driver
#(
    .AXI_DATA_WIDTH           ( WBUF_AXI_DATA_WIDTH                   ),
    .OP_WIDTH                 ( WBUF_AXI_DATA_WIDTH                 ),
    .NUM_PE                   ( 32                   ),
    .BASE_ADDR                (32'h0000_0000             ),
    .TX_SIZE_WIDTH            ( 25            )
) wbuf_axim_driver (
    .clk                      ( clk                      ),
    .reset                    ( reset                    ),     
    .M_AXI_AWID               ( 0               ),   
    .M_AXI_AWADDR             ( cl_ddr2_awaddr  ),   
    .M_AXI_AWLEN              ( cl_ddr2_awlen   ),   
    .M_AXI_AWSIZE             ( cl_ddr2_awsize  ),   
    .M_AXI_AWBURST            ( cl_ddr2_awburst ),   
    .M_AXI_AWLOCK             ( 0               ),   
    .M_AXI_AWCACHE            ( 0               ),   
    .M_AXI_AWPROT             ( 0               ),   
    .M_AXI_AWQOS              ( 0               ),   
    .M_AXI_AWVALID            ( cl_ddr2_awvalid ),   
    .M_AXI_AWREADY            ( cl_ddr2_awready ),   
    .M_AXI_WID                ( 0               ),   
    .M_AXI_WDATA              ( cl_ddr2_wdata   ),   
    .M_AXI_WSTRB              ( cl_ddr2_wstrb   ),   
    .M_AXI_WLAST              ( cl_ddr2_wlast   ),   
    .M_AXI_WVALID             ( cl_ddr2_wvalid  ),   
    .M_AXI_WREADY             ( cl_ddr2_wready  ),   
    .M_AXI_BID                (                 ),   
    .M_AXI_BRESP              ( cl_ddr2_bresp   ),   
    .M_AXI_BVALID             ( cl_ddr2_bvalid  ),   
    .M_AXI_BREADY             ( cl_ddr2_bready  ),   
    .M_AXI_ARID               ( cl_ddr2_rid     ),   
    .M_AXI_ARADDR             ( cl_ddr2_araddr  ),   
    .M_AXI_ARLEN              ( cl_ddr2_arlen   ),   
    .M_AXI_ARSIZE             ( cl_ddr2_arsize  ),   
    .M_AXI_ARBURST            ( cl_ddr2_arburst ),   
    .M_AXI_ARLOCK             ( 0               ),   
    .M_AXI_ARCACHE            ( 0               ),
    .M_AXI_ARPROT             ( 0               ),
    .M_AXI_ARQOS              ( 0               ),
    .M_AXI_ARVALID            ( cl_ddr2_arvalid ),
    .M_AXI_ARREADY            ( cl_ddr2_arready ),
    .M_AXI_RID                ( cl_ddr2_arid    ),
    .M_AXI_RDATA              ( cl_ddr2_rdata   ),
    .M_AXI_RRESP              ( cl_ddr2_rresp   ),
    .M_AXI_RLAST              ( cl_ddr2_rlast   ),
    .M_AXI_RVALID             ( cl_ddr2_rvalid  ),
    .M_AXI_RREADY             ( cl_ddr2_rready  )
);

axi_master_tb_driver
#(
    .AXI_DATA_WIDTH           ( BBUF_AXI_DATA_WIDTH                   ),
    .OP_WIDTH                 ( BBUF_AXI_DATA_WIDTH                 ),
    .NUM_PE                   ( 32                   ),
    .BASE_ADDR                (32'h0000_0000),
    .TX_SIZE_WIDTH            ( 25            )
) bbuf_axim_driver (
    .clk                      ( clk                      ),
    .reset                    ( reset                    ),     
    .M_AXI_AWID               ( 0               ),   
    .M_AXI_AWADDR             ( cl_ddr3_awaddr  ),   
    .M_AXI_AWLEN              ( cl_ddr3_awlen   ),   
    .M_AXI_AWSIZE             ( cl_ddr3_awsize  ),   
    .M_AXI_AWBURST            ( cl_ddr3_awburst ),   
    .M_AXI_AWLOCK             ( 0               ),   
    .M_AXI_AWCACHE            ( 0               ),   
    .M_AXI_AWPROT             ( 0               ),   
    .M_AXI_AWQOS              ( 0               ),   
    .M_AXI_AWVALID            ( cl_ddr3_awvalid ),   
    .M_AXI_AWREADY            ( cl_ddr3_awready ),   
    .M_AXI_WID                ( 0               ),   
    .M_AXI_WDATA              ( cl_ddr3_wdata   ),   
    .M_AXI_WSTRB              ( cl_ddr3_wstrb   ),   
    .M_AXI_WLAST              ( cl_ddr3_wlast   ),   
    .M_AXI_WVALID             ( cl_ddr3_wvalid  ),   
    .M_AXI_WREADY             ( cl_ddr3_wready  ),   
    .M_AXI_BID                (                 ),   
    .M_AXI_BRESP              ( cl_ddr3_bresp   ),   
    .M_AXI_BVALID             ( cl_ddr3_bvalid  ),   
    .M_AXI_BREADY             ( cl_ddr3_bready  ),   
    .M_AXI_ARID               ( cl_ddr3_rid     ),   
    .M_AXI_ARADDR             ( cl_ddr3_araddr  ),   
    .M_AXI_ARLEN              ( cl_ddr3_arlen   ),   
    .M_AXI_ARSIZE             ( cl_ddr3_arsize  ),   
    .M_AXI_ARBURST            ( cl_ddr3_arburst ),   
    .M_AXI_ARLOCK             ( 0               ),   
    .M_AXI_ARCACHE            ( 0               ),
    .M_AXI_ARPROT             ( 0               ),
    .M_AXI_ARQOS              ( 0               ),
    .M_AXI_ARVALID            ( cl_ddr3_arvalid ),
    .M_AXI_ARREADY            ( cl_ddr3_arready ),
    .M_AXI_RID                ( cl_ddr3_arid    ),
    .M_AXI_RDATA              ( cl_ddr3_rdata   ),
    .M_AXI_RRESP              ( cl_ddr3_rresp   ),
    .M_AXI_RLAST              ( cl_ddr3_rlast   ),
    .M_AXI_RVALID             ( cl_ddr3_rvalid  ),
    .M_AXI_RREADY             ( cl_ddr3_rready  )
);
axi_master_tb_driver
#(
    .AXI_DATA_WIDTH           ( OBUF_AXI_DATA_WIDTH                   ),
    .OP_WIDTH                 ( OBUF_AXI_DATA_WIDTH                 ),
    .NUM_PE                   ( 32                   ),
    .BASE_ADDR                (32'h0000_0000             ),
    .TX_SIZE_WIDTH            ( 25            )
) obuf_axim_driver (
    .clk                      ( clk                      ),
    .reset                    ( reset                    ),     
    .M_AXI_AWID               ( 0               ),   
    .M_AXI_AWADDR             ( cl_ddr1_awaddr  ),   
    .M_AXI_AWLEN              ( cl_ddr1_awlen   ),   
    .M_AXI_AWSIZE             ( cl_ddr1_awsize  ),   
    .M_AXI_AWBURST            ( cl_ddr1_awburst ),   
    .M_AXI_AWLOCK             ( 0               ),   
    .M_AXI_AWCACHE            ( 0               ),   
    .M_AXI_AWPROT             ( 0               ),   
    .M_AXI_AWQOS              ( 0               ),   
    .M_AXI_AWVALID            ( cl_ddr1_awvalid ),   
    .M_AXI_AWREADY            ( cl_ddr1_awready ),   
    .M_AXI_WID                ( 0               ),   
    .M_AXI_WDATA              ( cl_ddr1_wdata   ),   
    .M_AXI_WSTRB              ( cl_ddr1_wstrb   ),   
    .M_AXI_WLAST              ( cl_ddr1_wlast   ),   
    .M_AXI_WVALID             ( cl_ddr1_wvalid  ),   
    .M_AXI_WREADY             ( cl_ddr1_wready  ),   
    .M_AXI_BID                (                 ),   
    .M_AXI_BRESP              ( cl_ddr1_bresp   ),   
    .M_AXI_BVALID             ( cl_ddr1_bvalid  ),   
    .M_AXI_BREADY             ( cl_ddr1_bready  ),   
    .M_AXI_ARID               ( cl_ddr1_rid     ),   
    .M_AXI_ARADDR             ( cl_ddr1_araddr  ),   
    .M_AXI_ARLEN              ( cl_ddr1_arlen   ),   
    .M_AXI_ARSIZE             ( cl_ddr1_arsize  ),   
    .M_AXI_ARBURST            ( cl_ddr1_arburst ),   
    .M_AXI_ARLOCK             ( 0               ),   
    .M_AXI_ARCACHE            ( 0               ),
    .M_AXI_ARPROT             ( 0               ),
    .M_AXI_ARQOS              ( 0               ),
    .M_AXI_ARVALID            ( cl_ddr1_arvalid ),
    .M_AXI_ARREADY            ( cl_ddr1_arready ),
    .M_AXI_RID                ( cl_ddr1_arid    ),
    .M_AXI_RDATA              ( cl_ddr1_rdata   ),
    .M_AXI_RRESP              ( cl_ddr1_rresp   ),
    .M_AXI_RLAST              ( cl_ddr1_rlast   ),
    .M_AXI_RVALID             ( cl_ddr1_rvalid  ),
    .M_AXI_RREADY             ( cl_ddr1_rready  )
);
axi_master_tb_driver
#(
    .AXI_DATA_WIDTH           ( PU_AXI_DATA_WIDTH                   ),
    .OP_WIDTH                 ( PU_AXI_DATA_WIDTH                 ),
    .NUM_PE                   ( 32                   ),
    .BASE_ADDR                (32'h0000_0000             ),
    .TX_SIZE_WIDTH            ( 25            )
) pubuf_axim_driver (
    .clk                      ( clk                      ),
    .reset                    ( reset                    ),     
    .M_AXI_AWID               ( 0               ),   
    .M_AXI_AWADDR             ( cl_ddr4_awaddr  ),   
    .M_AXI_AWLEN              ( cl_ddr4_awlen   ),   
    .M_AXI_AWSIZE             ( cl_ddr4_awsize  ),   
    .M_AXI_AWBURST            ( cl_ddr4_awburst ),   
    .M_AXI_AWLOCK             ( 0               ),   
    .M_AXI_AWCACHE            ( 0               ),   
    .M_AXI_AWPROT             ( 0               ),   
    .M_AXI_AWQOS              ( 0               ),   
    .M_AXI_AWVALID            ( cl_ddr4_awvalid ),   
    .M_AXI_AWREADY            ( cl_ddr4_awready ),   
    .M_AXI_WID                ( 0               ),   
    .M_AXI_WDATA              ( cl_ddr4_wdata   ),   
    .M_AXI_WSTRB              ( cl_ddr4_wstrb   ),   
    .M_AXI_WLAST              ( cl_ddr4_wlast   ),   
    .M_AXI_WVALID             ( cl_ddr4_wvalid  ),   
    .M_AXI_WREADY             ( cl_ddr4_wready  ),   
    .M_AXI_BID                (                 ),   
    .M_AXI_BRESP              ( cl_ddr4_bresp   ),   
    .M_AXI_BVALID             ( cl_ddr4_bvalid  ),   
    .M_AXI_BREADY             ( cl_ddr4_bready  ),   
    .M_AXI_ARID               ( cl_ddr4_rid     ),   
    .M_AXI_ARADDR             ( cl_ddr4_araddr  ),   
    .M_AXI_ARLEN              ( cl_ddr4_arlen   ),   
    .M_AXI_ARSIZE             ( cl_ddr4_arsize  ),   
    .M_AXI_ARBURST            ( cl_ddr4_arburst ),   
    .M_AXI_ARLOCK             ( 0               ),   
    .M_AXI_ARCACHE            ( 0               ),
    .M_AXI_ARPROT             ( 0               ),
    .M_AXI_ARQOS              ( 0               ),
    .M_AXI_ARVALID            ( cl_ddr4_arvalid ),
    .M_AXI_ARREADY            ( cl_ddr4_arready ),
    .M_AXI_RID                ( cl_ddr4_arid    ),
    .M_AXI_RDATA              ( cl_ddr4_rdata   ),
    .M_AXI_RRESP              ( cl_ddr4_rresp   ),
    .M_AXI_RLAST              ( cl_ddr4_rlast   ),
    .M_AXI_RVALID             ( cl_ddr4_rvalid  ),
    .M_AXI_RREADY             ( cl_ddr4_rready  )
);
dnnweaver2_controller UUT 
 (
    .clk                 ( clk                ),
    .reset               ( reset              ),
    .start               ( start              ),
    .num_blocks_in       ( num_blocks_in      ),
    .pci_cl_ctrl_awvalid ( pci_cl_ctrl_awvalid),
    .pci_cl_ctrl_awaddr  ( pci_cl_ctrl_awaddr ),
    .pci_cl_ctrl_awready ( pci_cl_ctrl_awready),
    .pci_cl_ctrl_wvalid  ( pci_cl_ctrl_wvalid ),
    .pci_cl_ctrl_wdata   ( pci_cl_ctrl_wdata  ),
    .pci_cl_ctrl_wstrb   ( pci_cl_ctrl_wstrb  ),
    .pci_cl_ctrl_wready  ( pci_cl_ctrl_wready ),
    .pci_cl_ctrl_bvalid  ( pci_cl_ctrl_bvalid ),
    .pci_cl_ctrl_bresp   ( pci_cl_ctrl_bresp  ),
    .pci_cl_ctrl_bready  ( pci_cl_ctrl_bready ),
    .pci_cl_ctrl_arvalid ( pci_cl_ctrl_arvalid),
    .pci_cl_ctrl_araddr  ( pci_cl_ctrl_araddr ),
    .pci_cl_ctrl_arready ( pci_cl_ctrl_arready),
    .pci_cl_ctrl_rvalid  ( pci_cl_ctrl_rvalid ),
    .pci_cl_ctrl_rdata   ( pci_cl_ctrl_rdata  ),
    .pci_cl_ctrl_rresp   ( pci_cl_ctrl_rresp  ),
    .pci_cl_ctrl_rready  ( pci_cl_ctrl_rready ),
    .pci_cl_data_awaddr  ( pci_cl_data_awaddr ),
    .pci_cl_data_awlen   ( pci_cl_data_awlen  ),
    .pci_cl_data_awsize  ( pci_cl_data_awsize ),
    .pci_cl_data_awburst ( pci_cl_data_awburst),
    .pci_cl_data_awvalid ( pci_cl_data_awvalid),
    .pci_cl_data_awready ( pci_cl_data_awready),
    .pci_cl_data_wdata   ( pci_cl_data_wdata  ),
    .pci_cl_data_wstrb   ( pci_cl_data_wstrb  ),
    .pci_cl_data_wlast   ( pci_cl_data_wlast  ),
    .pci_cl_data_wvalid  ( pci_cl_data_wvalid ),
    .pci_cl_data_wready  ( pci_cl_data_wready ),
    .pci_cl_data_bresp   ( pci_cl_data_bresp  ),
    .pci_cl_data_bvalid  ( pci_cl_data_bvalid ),
    .pci_cl_data_bready  ( pci_cl_data_bready ),
    .pci_cl_data_araddr  ( pci_cl_data_araddr ),
    .pci_cl_data_arlen   ( pci_cl_data_arlen  ),
    .pci_cl_data_arsize  ( pci_cl_data_arsize ),
    .pci_cl_data_arburst ( pci_cl_data_arburst),
    .pci_cl_data_arvalid ( pci_cl_data_arvalid),
    .pci_cl_data_arready ( pci_cl_data_arready),
    .pci_cl_data_rdata   ( pci_cl_data_rdata  ),
    .pci_cl_data_rresp   ( pci_cl_data_rresp  ),
    .pci_cl_data_rlast   ( pci_cl_data_rlast  ),
    .pci_cl_data_rvalid  ( pci_cl_data_rvalid ),
    .pci_cl_data_rready  ( pci_cl_data_rready ),
    .cl_ddr0_awaddr      ( cl_ddr0_awaddr     ),
    .cl_ddr0_awlen       ( cl_ddr0_awlen      ),
    .cl_ddr0_awsize      ( cl_ddr0_awsize     ),
    .cl_ddr0_awburst     ( cl_ddr0_awburst    ),
    .cl_ddr0_awvalid     ( cl_ddr0_awvalid    ),
    .cl_ddr0_awready     ( cl_ddr0_awready    ),
    .cl_ddr0_wdata       ( cl_ddr0_wdata      ),
    .cl_ddr0_wstrb       ( cl_ddr0_wstrb      ),
    .cl_ddr0_wlast       ( cl_ddr0_wlast      ),
    .cl_ddr0_wvalid      ( cl_ddr0_wvalid     ),
    .cl_ddr0_wready      ( cl_ddr0_wready     ),
    .cl_ddr0_bresp       ( cl_ddr0_bresp      ),
    .cl_ddr0_bvalid      ( cl_ddr0_bvalid     ),
    .cl_ddr0_bready      ( cl_ddr0_bready     ),
    .cl_ddr0_araddr      ( cl_ddr0_araddr     ),
    .cl_ddr0_arlen       ( cl_ddr0_arlen      ),
    .cl_ddr0_arsize      ( cl_ddr0_arsize     ),
    .cl_ddr0_arburst     ( cl_ddr0_arburst    ),
    .cl_ddr0_arvalid     ( cl_ddr0_arvalid    ),
    .cl_ddr0_arid        ( cl_ddr0_arid       ),
    .cl_ddr0_arready     ( cl_ddr0_arready    ),
    .cl_ddr0_rdata       ( cl_ddr0_rdata      ),
    .cl_ddr0_rid         ( cl_ddr0_rid        ),
    .cl_ddr0_rresp       ( cl_ddr0_rresp      ),
    .cl_ddr0_rlast       ( cl_ddr0_rlast      ),
    .cl_ddr0_rvalid      ( cl_ddr0_rvalid     ),
    .cl_ddr0_rready      ( cl_ddr0_rready     ),
    .cl_ddr1_awaddr      ( cl_ddr1_awaddr     ),
    .cl_ddr1_awlen       ( cl_ddr1_awlen      ),
    .cl_ddr1_awsize      ( cl_ddr1_awsize     ),
    .cl_ddr1_awburst     ( cl_ddr1_awburst    ),
    .cl_ddr1_awvalid     ( cl_ddr1_awvalid    ),
    .cl_ddr1_awready     ( cl_ddr1_awready    ),
    .cl_ddr1_wdata       ( cl_ddr1_wdata      ),
    .cl_ddr1_wstrb       ( cl_ddr1_wstrb      ),
    .cl_ddr1_wlast       ( cl_ddr1_wlast      ),
    .cl_ddr1_wvalid      ( cl_ddr1_wvalid     ),
    .cl_ddr1_wready      ( cl_ddr1_wready     ),
    .cl_ddr1_bresp       ( cl_ddr1_bresp      ),
    .cl_ddr1_bvalid      ( cl_ddr1_bvalid     ),
    .cl_ddr1_bready      ( cl_ddr1_bready     ),
    .cl_ddr1_araddr      ( cl_ddr1_araddr     ),
    .cl_ddr1_arlen       ( cl_ddr1_arlen      ),
    .cl_ddr1_arsize      ( cl_ddr1_arsize     ),
    .cl_ddr1_arburst     ( cl_ddr1_arburst    ),
    .cl_ddr1_arvalid     ( cl_ddr1_arvalid    ),
    .cl_ddr1_arid        ( cl_ddr1_arid       ),
    .cl_ddr1_arready     ( cl_ddr1_arready    ),
    .cl_ddr1_rdata       ( cl_ddr1_rdata      ),
    .cl_ddr1_rid         ( cl_ddr1_rid        ),
    .cl_ddr1_rresp       ( cl_ddr1_rresp      ),
    .cl_ddr1_rlast       ( cl_ddr1_rlast      ),
    .cl_ddr1_rvalid      ( cl_ddr1_rvalid     ),
    .cl_ddr1_rready      ( cl_ddr1_rready     ),
    .cl_ddr2_awaddr      ( cl_ddr2_awaddr     ),
    .cl_ddr2_awlen       ( cl_ddr2_awlen      ),
    .cl_ddr2_awsize      ( cl_ddr2_awsize     ),
    .cl_ddr2_awburst     ( cl_ddr2_awburst    ),
    .cl_ddr2_awvalid     ( cl_ddr2_awvalid    ),
    .cl_ddr2_awready     ( cl_ddr2_awready    ),
    .cl_ddr2_wdata       ( cl_ddr2_wdata      ),
    .cl_ddr2_wstrb       ( cl_ddr2_wstrb      ),
    .cl_ddr2_wlast       ( cl_ddr2_wlast      ),
    .cl_ddr2_wvalid      ( cl_ddr2_wvalid     ),
    .cl_ddr2_wready      ( cl_ddr2_wready     ),
    .cl_ddr2_bresp       ( cl_ddr2_bresp      ),
    .cl_ddr2_bvalid      ( cl_ddr2_bvalid     ),
    .cl_ddr2_bready      ( cl_ddr2_bready     ),
    .cl_ddr2_araddr      ( cl_ddr2_araddr     ),
    .cl_ddr2_arlen       ( cl_ddr2_arlen      ),
    .cl_ddr2_arsize      ( cl_ddr2_arsize     ),
    .cl_ddr2_arburst     ( cl_ddr2_arburst    ),
    .cl_ddr2_arvalid     ( cl_ddr2_arvalid    ),
    .cl_ddr2_arid        ( cl_ddr2_arid       ),
    .cl_ddr2_arready     ( cl_ddr2_arready    ),
    .cl_ddr2_rdata       ( cl_ddr2_rdata      ),
    .cl_ddr2_rid         ( cl_ddr2_rid        ),
    .cl_ddr2_rresp       ( cl_ddr2_rresp      ),
    .cl_ddr2_rlast       ( cl_ddr2_rlast      ),
    .cl_ddr2_rvalid      ( cl_ddr2_rvalid     ),
    .cl_ddr2_rready      ( cl_ddr2_rready     ),
    .cl_ddr3_awaddr      ( cl_ddr3_awaddr     ),
    .cl_ddr3_awlen       ( cl_ddr3_awlen      ),
    .cl_ddr3_awsize      ( cl_ddr3_awsize     ),
    .cl_ddr3_awburst     ( cl_ddr3_awburst    ),
    .cl_ddr3_awvalid     ( cl_ddr3_awvalid    ),
    .cl_ddr3_awready     ( cl_ddr3_awready    ),
    .cl_ddr3_wdata       ( cl_ddr3_wdata      ),
    .cl_ddr3_wstrb       ( cl_ddr3_wstrb      ),
    .cl_ddr3_wlast       ( cl_ddr3_wlast      ),
    .cl_ddr3_wvalid      ( cl_ddr3_wvalid     ),
    .cl_ddr3_wready      ( cl_ddr3_wready     ),
    .cl_ddr3_bresp       ( cl_ddr3_bresp      ),
    .cl_ddr3_bvalid      ( cl_ddr3_bvalid     ),
    .cl_ddr3_bready      ( cl_ddr3_bready     ),
    .cl_ddr3_araddr      ( cl_ddr3_araddr     ),
    .cl_ddr3_arlen       ( cl_ddr3_arlen      ),
    .cl_ddr3_arsize      ( cl_ddr3_arsize     ),
    .cl_ddr3_arburst     ( cl_ddr3_arburst    ),
    .cl_ddr3_arvalid     ( cl_ddr3_arvalid    ),
    .cl_ddr3_arid        ( cl_ddr3_arid       ),
    .cl_ddr3_arready     ( cl_ddr3_arready    ),
    .cl_ddr3_rdata       ( cl_ddr3_rdata      ),
    .cl_ddr3_rid         ( cl_ddr3_rid        ),
    .cl_ddr3_rresp       ( cl_ddr3_rresp      ),
    .cl_ddr3_rlast       ( cl_ddr3_rlast      ),
    .cl_ddr3_rvalid      ( cl_ddr3_rvalid     ),
    .cl_ddr3_rready      ( cl_ddr3_rready     ),
    .cl_ddr4_awaddr      ( cl_ddr4_awaddr     ),
    .cl_ddr4_awlen       ( cl_ddr4_awlen      ),
    .cl_ddr4_awsize      ( cl_ddr4_awsize     ),
    .cl_ddr4_awburst     ( cl_ddr4_awburst    ),
    .cl_ddr4_awvalid     ( cl_ddr4_awvalid    ),
    .cl_ddr4_awready     ( cl_ddr4_awready    ),
    .cl_ddr4_wdata       ( cl_ddr4_wdata      ),
    .cl_ddr4_wstrb       ( cl_ddr4_wstrb      ),
    .cl_ddr4_wlast       ( cl_ddr4_wlast      ),
    .cl_ddr4_wvalid      ( cl_ddr4_wvalid     ),
    .cl_ddr4_wready      ( cl_ddr4_wready     ),
    .cl_ddr4_bresp       ( cl_ddr4_bresp      ),
    .cl_ddr4_bvalid      ( cl_ddr4_bvalid     ),
    .cl_ddr4_bready      ( cl_ddr4_bready     ),
    .cl_ddr4_araddr      ( cl_ddr4_araddr     ),
    .cl_ddr4_arlen       ( cl_ddr4_arlen      ),
    .cl_ddr4_arsize      ( cl_ddr4_arsize     ),
    .cl_ddr4_arburst     ( cl_ddr4_arburst    ),
    .cl_ddr4_arvalid     ( cl_ddr4_arvalid    ),
    .cl_ddr4_arid        ( cl_ddr4_arid       ),
    .cl_ddr4_arready     ( cl_ddr4_arready    ),
    .cl_ddr4_rdata       ( cl_ddr4_rdata      ),
    .cl_ddr4_rid         ( cl_ddr4_rid        ),
    .cl_ddr4_rresp       ( cl_ddr4_rresp      ),
    .cl_ddr4_rlast       ( cl_ddr4_rlast      ),
    .cl_ddr4_rvalid      ( cl_ddr4_rvalid     ),
    .cl_ddr4_rready      ( cl_ddr4_rready     )
  );


parameter IMGSTARTADDR  = 32'h5000 >> 1; 
parameter IMGSIZE     =  40000 ;


parameter OPADDR= 32'h13000>>1;
parameter SIZE =4;


integer ii;
integer fp;
integer addr;
  initial begin
          sel=0;
	  reset=1;
	  start=0;
	  clk=0;
	  num_blocks_in=0;

	  #100;
	  #50;
          reset=0;
	  #50 ;
	  @(negedge clk);
	  num_blocks_in=113;
	  #20;
	  @(negedge clk);
	  start=1;
	  @(negedge clk);
	  start=0;
 	 $display("started dnnweaver2 operations...."); 
         wait(UUT.u_ctrl.block_done==1);
         #20;
	 $display("conv0 completed"); 
         wait(UUT.u_ctrl.block_done==1);
         #20;
	 $display("conv1 completed"); 
     /*    wait(UUT.u_ctrl.block_done==1);
         #20;
	 $display("fc1 completed"); 
         wait(UUT.u_ctrl.block_done==1);
	 $display("fc2 completed"); 
*/
	// display the ddr_ram contents 
         $display("ibuf ddr contents\n"	); 
         addr= IMGSTARTADDR;  
         for(ii=0;ii<1000;ii=ii+1) begin
          $display("ddr_ram[%x]=%x",addr+ii,ibuf_axim_driver.ddr_ram[addr+ii]); 
  	 end 
	
  /*       $display("FC2 Final Output\n\r");
         addr= OPADDR;  
         for(ii=0;ii<SIZE;ii=ii+1) begin
          $display("ddr_ram[%x]=%x\n",addr+ii,pubuf_axim_driver.ddr_ram[addr+ii]); 

         end
    */     #10000;
         $finish;
	  
  end
  always #2 clk=~clk;

 reg [15:0] imemcount = (1 << 12); 
 integer i; 

 initial begin

    $dumpfile("tb_dnnw2_ctrl.vcd");
    $dumpvars(0,tb_dnnw2_ctrl);
   // record the memory contents in vcd 
   // intruction memory contents 
   for (i = 0; i < imemcount; i = i + 1) begin 
     $dumpvars(1, tb_dnnw2_ctrl.UUT.u_ctrl.imem.mem[i]);
   end
   // base (outer loop) controller mem blocks  
   for (i = 0; i < 32; i = i + 1) begin 
     $dumpvars(1, tb_dnnw2_ctrl.UUT.u_ctrl.base_ctrl.mws_ibuf_ld.offset_buf.mem[i]);
     $dumpvars(1, tb_dnnw2_ctrl.UUT.u_ctrl.base_ctrl.mws_ibuf_ld.stride_buf.mem[i]);
	
     $dumpvars(1, tb_dnnw2_ctrl.UUT.u_ctrl.base_ctrl.mws_wbuf_ld.offset_buf.mem[i]);
     $dumpvars(1, tb_dnnw2_ctrl.UUT.u_ctrl.base_ctrl.mws_wbuf_ld.stride_buf.mem[i]);

     $dumpvars(1, tb_dnnw2_ctrl.UUT.u_ctrl.base_ctrl.mws_obuf_ld.offset_buf.mem[i]);
     $dumpvars(1, tb_dnnw2_ctrl.UUT.u_ctrl.base_ctrl.mws_obuf_ld.stride_buf.mem[i]);


     $dumpvars(1, tb_dnnw2_ctrl.UUT.u_ctrl.base_ctrl.base_loop_ctrl.iter_buf.mem[i]);
     $dumpvars(1, tb_dnnw2_ctrl.UUT.u_ctrl.base_ctrl.base_loop_ctrl.loop_buf.mem[i]);

   end


   // base (outer loop) controller mem blocks  
   for (i = 0; i < 32; i = i + 1) begin 
     $dumpvars(1, tb_dnnw2_ctrl.UUT.compute_ctrl.mws_ibuf_ld.offset_buf.mem[i]);
     $dumpvars(1, tb_dnnw2_ctrl.UUT.compute_ctrl.mws_ibuf_ld.stride_buf.mem[i]);
	
     $dumpvars(1, tb_dnnw2_ctrl.UUT.compute_ctrl.mws_wbuf_ld.offset_buf.mem[i]);
     $dumpvars(1, tb_dnnw2_ctrl.UUT.compute_ctrl.mws_wbuf_ld.stride_buf.mem[i]);

     $dumpvars(1, tb_dnnw2_ctrl.UUT.compute_ctrl.mws_obuf_ld.offset_buf.mem[i]);
     $dumpvars(1, tb_dnnw2_ctrl.UUT.compute_ctrl.mws_obuf_ld.stride_buf.mem[i]);


     $dumpvars(1, tb_dnnw2_ctrl.UUT.compute_ctrl.base_loop_ctrl.iter_buf.mem[i]);
     $dumpvars(1, tb_dnnw2_ctrl.UUT.compute_ctrl.base_loop_ctrl.loop_buf.mem[i]);

   end




 end


endmodule
