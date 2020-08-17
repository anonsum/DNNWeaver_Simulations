make clean
mkdir simoutputs 
make compile
vvp -v -M /home/anonsum/iverilog/install/lib/ivl -l sim.log compiler.out 
mv sim.log compiler.out *.vcd simoutputs
mv conv1*.txt conv2*.txt ip*.txt simoutputs
