FILELIST = filelist.tb
SRC := $(shell cat $(FILELIST) | egrep -v '\#')

COMPILER = iverilog
COMPILER_FLAGS = #-Wall
COMPILER_OUTPUT = compiler.out
INCLUDE_PATH= . 

#TOP_MODULE= pooling_tb
#TOP_MODULE= controller_tb
TOP_MODULE=tb_dnnw2_ctrl

SIMULATOR = vvp
SIMULATOR_FLAGS = -vcd
WAVEFORM = TB.vcd

WAVEFORM_VIEWER = gtkwave
###############################################################################
all: simulate

compile: $(SRC) $(FILELIST)
	$(COMPILER) $(COMPILER_FLAGS) -c $(FILELIST) -g2012  -o $(COMPILER_OUTPUT) -Dsimulation -I $(INCLUDE_PATH) -s $(TOP_MODULE)

simulate: $(COMPILER_OUTPUT) $(SRC) $(FILELIST)
	$(SIMULATOR) $(SOPTIONS) $(COMPILER_OUTPUT) $(SIMULATOR_FLAGS)

display: $(WAVEFORM)
	$(WAVEFORM_VIEWER) $(WAVEFORM) &

$(WAVEFORM): $(COMPILER_OUTPUT) $(SRC) $(FILELIST)
	$(SIMULATOR) $(SOPTIONS) $(COMPILER_OUTPUT) $(SIMULATOR_FLAGS)

$(COMPILER_OUTPUT): $(SRC) $(FILELIST)
	$(COMPILER) $(COMPILER_FLAGS) -c $(FILELIST) -g2012 -o $(COMPILER_OUTPUT) -I $(INCLUDE_PATH) 

clean: 
	\rm $(WAVEFORM) $(COMPILER_OUTPUT)
