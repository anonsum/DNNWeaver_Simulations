//
// Instruction Memory
//
// Hardik Sharma
// (hsharma@gatech.edu)
`timescale 1ns/1ps

module instruction_memory_noPCI
#(
    parameter integer  DATA_WIDTH                   = 32,
    parameter integer  SIZE_IN_BITS                 = 1<<16,
    parameter integer  ADDR_WIDTH                   = $clog2(SIZE_IN_BITS/DATA_WIDTH),
  // Instructions
    parameter integer  INST_DATA_WIDTH              = 32,
    parameter integer  INST_ADDR_WIDTH              = 32,
    parameter integer  INST_WSTRB_WIDTH             = INST_DATA_WIDTH/8,
    parameter integer  INST_BURST_WIDTH             = 8
)
(
  // clk, reset
    input  wire                                         clk,
    input  wire                                         reset,

  // Decoder <- imem
    input  wire                                         s_read_req_b,
    input  wire  [ ADDR_WIDTH           -1 : 0 ]        s_read_addr_b,
    output wire  [ DATA_WIDTH           -1 : 0 ]        s_read_data_b

);

//=============================================================
// Localparams
//=============================================================

  // RD count
    localparam          R_COUNT_W                    = INST_BURST_WIDTH + 1;
  // Bytes per word
    localparam BYTES_PER_WORD = DATA_WIDTH / 8;
    localparam BYTE_ADDR_W = $clog2(BYTES_PER_WORD);
//=============================================================

//=============================================================
// Wires/Regs
//=============================================================
  // Host <-> imem
    wire                                        s_req_a;
    wire                                        s_wr_en_a;
    wire [ DATA_WIDTH           -1 : 0 ]        s_read_data_a;
    wire [ ADDR_WIDTH           -1 : 0 ]        s_read_addr_a;
    wire [ DATA_WIDTH           -1 : 0 ]        s_write_data_a;
    wire [ ADDR_WIDTH           -1 : 0 ]        s_write_addr_a;
  // FSM for writes to instruction memory (imem)
//    reg  [ STATE_W              -1 : 0 ]        imem_state_q;
//    reg  [ STATE_W              -1 : 0 ]        imem_state_d;
  // writes address for instruction memory (imem)
    reg  [ INST_ADDR_WIDTH      -1 : 0 ]        w_addr_d;
    reg  [ INST_ADDR_WIDTH      -1 : 0 ]        w_addr_q;

  // read address for instruction memory (imem)
    reg  [ INST_ADDR_WIDTH      -1 : 0 ]        r_addr_d;
    reg  [ INST_ADDR_WIDTH      -1 : 0 ]        r_addr_q;
  // read counter
    reg  [ R_COUNT_W            -1 : 0 ]        r_count_d;
    reg  [ R_COUNT_W            -1 : 0 ]        r_count_q;
    reg  [ R_COUNT_W            -1 : 0 ]        r_count_max_d;
    reg  [ R_COUNT_W            -1 : 0 ]        r_count_max_q;

    reg  [ DATA_WIDTH           -1 : 0 ]        _s_read_data_a;
    reg  [ DATA_WIDTH           -1 : 0 ]        _s_read_data_b;
//=============================================================

//=============================================================
// Assigns
//=============================================================
/*
    assign s_read_data_a = _s_read_data_a;
    assign pci_cl_data_awready = imem_state_q == IMEM_WR_ADDR;
    assign pci_cl_data_wready = imem_state_q == IMEM_WR_DATA;

    assign pci_cl_data_bvalid = imem_state_q == IMEM_WR_DATA && pci_cl_data_wlast;
    assign pci_cl_data_bresp = 0;

    assign pci_cl_data_arready = imem_state_q == IMEM_RD_ADDR;
    assign pci_cl_data_rvalid = imem_state_q == IMEM_RD_DATA;
    assign pci_cl_data_rlast = imem_state_q == IMEM_RD_DATA && pci_cl_data_rready && r_count_q == r_count_max_q;


    assign s_write_addr_a = w_addr_q[INST_ADDR_WIDTH-1:BYTE_ADDR_W];
    assign s_write_data_a = pci_cl_data_wdata;

    assign s_read_addr_a = r_addr_q[INST_ADDR_WIDTH-1:BYTE_ADDR_W];
    assign s_req_a = ((imem_state_q == IMEM_RD_REQ ||
                     (imem_state_q == IMEM_RD_DATA && pci_cl_data_rready))
                     || (imem_state_q == IMEM_WR_DATA && pci_cl_data_wvalid));
    assign s_wr_en_a = imem_state_q == IMEM_WR_DATA;

    assign pci_cl_data_rdata = s_read_data_a;
    assign pci_cl_data_rresp = 2'b0;
//=============================================================

//=============================================================
// FSM
//=============================================================
  always @(*)
  begin: READ_FSM
    imem_state_d = imem_state_q;
    r_addr_d = r_addr_q;
    r_count_max_d = r_count_max_q;
    r_count_d = r_count_q;
    w_addr_d = w_addr_q;
    case(imem_state_q)
      IMEM_IDLE: begin
        if (pci_cl_data_awvalid)
        begin
          imem_state_d = IMEM_WR_ADDR;
        end else if (pci_cl_data_arvalid)
        begin
          imem_state_d = IMEM_RD_ADDR;
        end
      end
      IMEM_WR_ADDR: begin
        if (pci_cl_data_awvalid) begin
          w_addr_d = pci_cl_data_awaddr;
          imem_state_d = IMEM_WR_DATA;
        end
        else
          imem_state_d = IMEM_IDLE;
      end
      IMEM_WR_DATA: begin
        if (pci_cl_data_wlast)
          imem_state_d = IMEM_IDLE;
        if (pci_cl_data_wvalid)
          w_addr_d = w_addr_d + BYTES_PER_WORD;
      end
      IMEM_RD_ADDR: begin
        if (pci_cl_data_arvalid) begin
          r_addr_d = pci_cl_data_araddr;
          r_count_max_d = pci_cl_data_arlen;
          r_count_d = 0;
          imem_state_d = IMEM_RD_REQ;
        end
        else
          imem_state_d = IMEM_IDLE;
      end
      IMEM_RD_REQ: begin
        r_addr_d = r_addr_d + BYTES_PER_WORD;
        imem_state_d = IMEM_RD_DATA;
      end
      IMEM_RD_DATA: begin
        if (pci_cl_data_rlast)
          imem_state_d = IMEM_IDLE;
        if (pci_cl_data_rvalid && pci_cl_data_rready) begin
          r_addr_d = r_addr_d + BYTES_PER_WORD;
          r_count_d = r_count_d + 1'b1;
        end
      end
    endcase
  end

  always @(posedge clk)
  begin
    if (reset)
      imem_state_q <= IMEM_IDLE;
    else
      imem_state_q <= imem_state_d;
  end

  always @(posedge clk)
  begin
    if (reset)
      w_addr_q <= 0;
    else
      w_addr_q <= w_addr_d;
  end

  always @(posedge clk)
  begin
    if (reset)
      r_addr_q <= 0;
    else
      r_addr_q <= r_addr_d;
  end

  always @(posedge clk)
  begin
    if (reset)
      r_count_q <= 0;
    else
      r_count_q <= r_count_d;
  end

  always @(posedge clk)
  begin
    if (reset)
      r_count_max_q <= 0;
    else
      r_count_max_q <= r_count_max_d;
  end
  */
//=============================================================

//=============================================================
// Dual port ram
//=============================================================
  reg  [ DATA_WIDTH -1 : 0 ] mem [ 0 : 1<<ADDR_WIDTH ];

  /*always @(posedge clk)
  begin: RAM_WRITE_PORT_A
    if (s_req_a) begin
      if (s_wr_en_a)
        mem[s_write_addr_a] <= s_write_data_a;
      else
        _s_read_data_a <= mem[s_read_addr_a];
    end
  end
*/
  initial begin   
       //$readmemh("test.bin",mem,0,77);	 // 3x3 img 
       $readmemh("instruction.bin",mem,0,338);	        //
  end

  always @(posedge clk)
  begin: RAM_WRITE_PORT_B
    if (s_read_req_b) begin
        _s_read_data_b <= mem[s_read_addr_b];
    end
  end
    assign s_read_data_b = _s_read_data_b;
//=============================================================


//=============================================================
// VCD
//=============================================================
`ifdef COCOTB_TOPLEVEL_instruction_memory
  initial begin
    $dumpfile("instruction_memory.vcd");
    $dumpvars(0, instruction_memory);
  end
`endif
//=============================================================
endmodule
