make clean
rm -rf compiler.out
make compile
vvp -v -M /home/anonsum/iverilog/install/lib/ivl -l sim.log compiler.out 
