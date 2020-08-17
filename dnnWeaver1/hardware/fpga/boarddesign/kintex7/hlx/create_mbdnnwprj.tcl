set origin_dir "."
create_project dnnweaver $origin_dir/dnnweaver -part xc7k325tffg900-2
set_property board_part digilentinc.com:genesys2:part0:1.1 [current_project]
set_property target_language Verilog [current_project]

source mb_dnnaccel.tcl

generate_target all [get_files  $origin_dir/dnnweaver/dnnweaver.srcs/sources_1/bd/mb/mb.bd]

export_ip_user_files -of_objects [get_files $origin_dir/dnnweaver/dnnweaver.srcs/sources_1/bd/mb/mb.bd] -no_script -force -quiet
export_simulation -of_objects [get_files $origin_dir/dnnweaver/dnnweaver.srcs/sources_1/bd/mb/mb.bd] -directory $origin_dir/dnnweaver/dnnweaver.ip_user_files/sim_scripts -force -quiet

add_files $origin_dir/../../../hardware/include
add_files $origin_dir/../../../hardware/source

remove_files $origin_dir/../../../hardware/source/top/zynq_wrapper_4AXI.v
remove_files $origin_dir/../../../hardware/source/top/zynq_wrapper_1AXI.v
remove_files $origin_dir/../../../hardware/source/top/zynq_wrapper_loopback.v
remove_files $origin_dir/../../../hardware/source/top/zynq_wrapper.v
add_files -norecurse $origin_dir/files/zynq_wrapper.v

##### To use chipcscope,Uncomment. files/PU_controller.v  has some debug probes enabled
#remove_files $origin_dir/../../../hardware/source/PU/PU_controller.v
#add_files -norecurse $origin_dir/files/PU_controller.v

update_compile_order -fileset sources_1
update_compile_order -fileset sim_1
update_compile_order -fileset sources_1

set_property top zynq_wrapper [current_fileset]
update_compile_order -fileset sources_1

add_files -fileset constrs_1 -copy_to $origin_dir/dnnweaver/dnnweaver.srcs/constr_1 -norecurse $origin_dir/files/top.xdc

#### Synthesis to bitstream generation 
launch_runs impl_1 -to_step write_bitstream 


