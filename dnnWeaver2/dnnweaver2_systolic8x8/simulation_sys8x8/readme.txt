
1) Run DNN COmpiler and generate instruction.bin (print in hex) : ./run.sh >&run.log
2) copy instruction.bin to sim_project_8x8
3) Open instruction.bin and removed 0x from all lines
4) In first line replace 4800000 with 04800000
5) In  rtl/mxv/instruction_memory_noPCI.v, line 217, modify the number of instructions field
6) In tb/axi_master_tb_driver.v, line 203 update the base address for Img,Weight,ibuf and obuf (from  ../dnnweaver2-master/run.log )
 
