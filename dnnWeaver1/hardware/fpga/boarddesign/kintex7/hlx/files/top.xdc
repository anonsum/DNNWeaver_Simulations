set_property IOSTANDARD LVDS [get_ports SYS_CLK_clk_n]
set_property PACKAGE_PIN AD11 [get_ports SYS_CLK_clk_n]
set_property PACKAGE_PIN AD12 [get_ports SYS_CLK_clk_p]
set_property IOSTANDARD LVDS [get_ports SYS_CLK_clk_p]
set_property PACKAGE_PIN R19 [get_ports sys_rst]
set_property IOSTANDARD LVCMOS33 [get_ports sys_rst]
set_property PACKAGE_PIN Y20 [get_ports UART_rxd]
set_property IOSTANDARD LVCMOS33 [get_ports UART_rxd]
set_property PACKAGE_PIN Y23 [get_ports UART_txd]
set_property IOSTANDARD LVCMOS33 [get_ports UART_txd]

set_property PACKAGE_PIN T28 [get_ports done_level]
set_property IOSTANDARD LVCMOS33 [get_ports done_level]
set_property PACKAGE_PIN U19 [get_ports start_level]
set_property IOSTANDARD LVCMOS33 [get_ports start_level]



create_debug_core u_ila_0 ila
set_property ALL_PROBE_SAME_MU true [get_debug_cores u_ila_0]
set_property ALL_PROBE_SAME_MU_CNT 1 [get_debug_cores u_ila_0]
set_property C_ADV_TRIGGER false [get_debug_cores u_ila_0]
set_property C_DATA_DEPTH 32768 [get_debug_cores u_ila_0]
set_property C_EN_STRG_QUAL false [get_debug_cores u_ila_0]
set_property C_INPUT_PIPE_STAGES 0 [get_debug_cores u_ila_0]
set_property C_TRIGIN_EN false [get_debug_cores u_ila_0]
set_property C_TRIGOUT_EN false [get_debug_cores u_ila_0]
set_property port_width 1 [get_debug_ports u_ila_0/clk]
connect_debug_port u_ila_0/clk [get_nets [list mb_i/mig_7series_0/u_mb_mig_7series_0_0_mig/u_ddr3_infrastructure/ui_addn_clk_1]]
set_property PROBE_TYPE DATA_AND_TRIGGER [get_debug_ports u_ila_0/probe0]
set_property port_width 32 [get_debug_ports u_ila_0/probe0]
connect_debug_port u_ila_0/probe0 [get_nets [list {M_AXI_GP0_awaddr[0]} {M_AXI_GP0_awaddr[1]} {M_AXI_GP0_awaddr[2]} {M_AXI_GP0_awaddr[3]} {M_AXI_GP0_awaddr[4]} {M_AXI_GP0_awaddr[5]} {M_AXI_GP0_awaddr[6]} {M_AXI_GP0_awaddr[7]} {M_AXI_GP0_awaddr[8]} {M_AXI_GP0_awaddr[9]} {M_AXI_GP0_awaddr[10]} {M_AXI_GP0_awaddr[11]} {M_AXI_GP0_awaddr[12]} {M_AXI_GP0_awaddr[13]} {M_AXI_GP0_awaddr[14]} {M_AXI_GP0_awaddr[15]} {M_AXI_GP0_awaddr[16]} {M_AXI_GP0_awaddr[17]} {M_AXI_GP0_awaddr[18]} {M_AXI_GP0_awaddr[19]} {M_AXI_GP0_awaddr[20]} {M_AXI_GP0_awaddr[21]} {M_AXI_GP0_awaddr[22]} {M_AXI_GP0_awaddr[23]} {M_AXI_GP0_awaddr[24]} {M_AXI_GP0_awaddr[25]} {M_AXI_GP0_awaddr[26]} {M_AXI_GP0_awaddr[27]} {M_AXI_GP0_awaddr[28]} {M_AXI_GP0_awaddr[29]} {M_AXI_GP0_awaddr[30]} {M_AXI_GP0_awaddr[31]}]]
create_debug_port u_ila_0 probe
set_property PROBE_TYPE DATA_AND_TRIGGER [get_debug_ports u_ila_0/probe1]
set_property port_width 32 [get_debug_ports u_ila_0/probe1]
connect_debug_port u_ila_0/probe1 [get_nets [list {M_AXI_GP0_wdata[0]} {M_AXI_GP0_wdata[1]} {M_AXI_GP0_wdata[2]} {M_AXI_GP0_wdata[3]} {M_AXI_GP0_wdata[4]} {M_AXI_GP0_wdata[5]} {M_AXI_GP0_wdata[6]} {M_AXI_GP0_wdata[7]} {M_AXI_GP0_wdata[8]} {M_AXI_GP0_wdata[9]} {M_AXI_GP0_wdata[10]} {M_AXI_GP0_wdata[11]} {M_AXI_GP0_wdata[12]} {M_AXI_GP0_wdata[13]} {M_AXI_GP0_wdata[14]} {M_AXI_GP0_wdata[15]} {M_AXI_GP0_wdata[16]} {M_AXI_GP0_wdata[17]} {M_AXI_GP0_wdata[18]} {M_AXI_GP0_wdata[19]} {M_AXI_GP0_wdata[20]} {M_AXI_GP0_wdata[21]} {M_AXI_GP0_wdata[22]} {M_AXI_GP0_wdata[23]} {M_AXI_GP0_wdata[24]} {M_AXI_GP0_wdata[25]} {M_AXI_GP0_wdata[26]} {M_AXI_GP0_wdata[27]} {M_AXI_GP0_wdata[28]} {M_AXI_GP0_wdata[29]} {M_AXI_GP0_wdata[30]} {M_AXI_GP0_wdata[31]}]]
create_debug_port u_ila_0 probe
set_property PROBE_TYPE DATA_AND_TRIGGER [get_debug_ports u_ila_0/probe2]
set_property port_width 32 [get_debug_ports u_ila_0/probe2]
connect_debug_port u_ila_0/probe2 [get_nets [list {S_AXI_HP0_araddr[0]} {S_AXI_HP0_araddr[1]} {S_AXI_HP0_araddr[2]} {S_AXI_HP0_araddr[3]} {S_AXI_HP0_araddr[4]} {S_AXI_HP0_araddr[5]} {S_AXI_HP0_araddr[6]} {S_AXI_HP0_araddr[7]} {S_AXI_HP0_araddr[8]} {S_AXI_HP0_araddr[9]} {S_AXI_HP0_araddr[10]} {S_AXI_HP0_araddr[11]} {S_AXI_HP0_araddr[12]} {S_AXI_HP0_araddr[13]} {S_AXI_HP0_araddr[14]} {S_AXI_HP0_araddr[15]} {S_AXI_HP0_araddr[16]} {S_AXI_HP0_araddr[17]} {S_AXI_HP0_araddr[18]} {S_AXI_HP0_araddr[19]} {S_AXI_HP0_araddr[20]} {S_AXI_HP0_araddr[21]} {S_AXI_HP0_araddr[22]} {S_AXI_HP0_araddr[23]} {S_AXI_HP0_araddr[24]} {S_AXI_HP0_araddr[25]} {S_AXI_HP0_araddr[26]} {S_AXI_HP0_araddr[27]} {S_AXI_HP0_araddr[28]} {S_AXI_HP0_araddr[29]} {S_AXI_HP0_araddr[30]} {S_AXI_HP0_araddr[31]}]]
create_debug_port u_ila_0 probe
set_property PROBE_TYPE DATA_AND_TRIGGER [get_debug_ports u_ila_0/probe3]
set_property port_width 4 [get_debug_ports u_ila_0/probe3]
connect_debug_port u_ila_0/probe3 [get_nets [list {S_AXI_HP0_arlen[0]} {S_AXI_HP0_arlen[1]} {S_AXI_HP0_arlen[2]} {S_AXI_HP0_arlen[3]}]]
create_debug_port u_ila_0 probe
set_property PROBE_TYPE DATA_AND_TRIGGER [get_debug_ports u_ila_0/probe4]
set_property port_width 32 [get_debug_ports u_ila_0/probe4]
connect_debug_port u_ila_0/probe4 [get_nets [list {S_AXI_HP0_awaddr[0]} {S_AXI_HP0_awaddr[1]} {S_AXI_HP0_awaddr[2]} {S_AXI_HP0_awaddr[3]} {S_AXI_HP0_awaddr[4]} {S_AXI_HP0_awaddr[5]} {S_AXI_HP0_awaddr[6]} {S_AXI_HP0_awaddr[7]} {S_AXI_HP0_awaddr[8]} {S_AXI_HP0_awaddr[9]} {S_AXI_HP0_awaddr[10]} {S_AXI_HP0_awaddr[11]} {S_AXI_HP0_awaddr[12]} {S_AXI_HP0_awaddr[13]} {S_AXI_HP0_awaddr[14]} {S_AXI_HP0_awaddr[15]} {S_AXI_HP0_awaddr[16]} {S_AXI_HP0_awaddr[17]} {S_AXI_HP0_awaddr[18]} {S_AXI_HP0_awaddr[19]} {S_AXI_HP0_awaddr[20]} {S_AXI_HP0_awaddr[21]} {S_AXI_HP0_awaddr[22]} {S_AXI_HP0_awaddr[23]} {S_AXI_HP0_awaddr[24]} {S_AXI_HP0_awaddr[25]} {S_AXI_HP0_awaddr[26]} {S_AXI_HP0_awaddr[27]} {S_AXI_HP0_awaddr[28]} {S_AXI_HP0_awaddr[29]} {S_AXI_HP0_awaddr[30]} {S_AXI_HP0_awaddr[31]}]]
create_debug_port u_ila_0 probe
set_property PROBE_TYPE DATA_AND_TRIGGER [get_debug_ports u_ila_0/probe5]
set_property port_width 3 [get_debug_ports u_ila_0/probe5]
connect_debug_port u_ila_0/probe5 [get_nets [list {accelerator/u_controller/state[0]} {accelerator/u_controller/state[1]} {accelerator/u_controller/state[2]}]]
create_debug_port u_ila_0 probe
set_property PROBE_TYPE DATA_AND_TRIGGER [get_debug_ports u_ila_0/probe6]
set_property port_width 10 [get_debug_ports u_ila_0/probe6]
connect_debug_port u_ila_0/probe6 [get_nets [list {accelerator/u_controller/l[0]} {accelerator/u_controller/l[1]} {accelerator/u_controller/l[2]} {accelerator/u_controller/l[3]} {accelerator/u_controller/l[4]} {accelerator/u_controller/l[5]} {accelerator/u_controller/l[6]} {accelerator/u_controller/l[7]} {accelerator/u_controller/l[8]} {accelerator/u_controller/l[9]}]]
create_debug_port u_ila_0 probe
set_property PROBE_TYPE DATA_AND_TRIGGER [get_debug_ports u_ila_0/probe7]
set_property port_width 1 [get_debug_ports u_ila_0/probe7]
connect_debug_port u_ila_0/probe7 [get_nets [list accelerator/u_controller/buffer_read_done]]
create_debug_port u_ila_0 probe
set_property PROBE_TYPE DATA_AND_TRIGGER [get_debug_ports u_ila_0/probe8]
set_property port_width 1 [get_debug_ports u_ila_0/probe8]
connect_debug_port u_ila_0/probe8 [get_nets [list done]]
create_debug_port u_ila_0 probe
set_property PROBE_TYPE DATA_AND_TRIGGER [get_debug_ports u_ila_0/probe9]
set_property port_width 1 [get_debug_ports u_ila_0/probe9]
connect_debug_port u_ila_0/probe9 [get_nets [list accelerator/u_controller/l_inc]]
create_debug_port u_ila_0 probe
set_property PROBE_TYPE DATA_AND_TRIGGER [get_debug_ports u_ila_0/probe10]
set_property port_width 1 [get_debug_ports u_ila_0/probe10]
connect_debug_port u_ila_0/probe10 [get_nets [list S_AXI_HP0_arready]]
create_debug_port u_ila_0 probe
set_property PROBE_TYPE DATA_AND_TRIGGER [get_debug_ports u_ila_0/probe11]
set_property port_width 1 [get_debug_ports u_ila_0/probe11]
connect_debug_port u_ila_0/probe11 [get_nets [list S_AXI_HP0_awready]]
create_debug_port u_ila_0 probe
set_property PROBE_TYPE DATA_AND_TRIGGER [get_debug_ports u_ila_0/probe12]
set_property port_width 1 [get_debug_ports u_ila_0/probe12]
connect_debug_port u_ila_0/probe12 [get_nets [list start]]
create_debug_port u_ila_0 probe
set_property PROBE_TYPE DATA_AND_TRIGGER [get_debug_ports u_ila_0/probe13]
set_property port_width 1 [get_debug_ports u_ila_0/probe13]
connect_debug_port u_ila_0/probe13 [get_nets [list accelerator/u_controller/vecgen_ready]]
set_property C_CLK_INPUT_FREQ_HZ 300000000 [get_debug_cores dbg_hub]
set_property C_ENABLE_CLK_DIVIDER false [get_debug_cores dbg_hub]
set_property C_USER_SCAN_CHAIN 1 [get_debug_cores dbg_hub]
connect_debug_port dbg_hub/clk [get_nets ACLK]
