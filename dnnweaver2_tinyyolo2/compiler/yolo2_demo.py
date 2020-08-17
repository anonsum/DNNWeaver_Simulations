###
###  First run to compile a YOLO network 
import logging
import numpy as np
import array
import math

#from dnnweaver2.benchmarks import get_graph
from dnnweaver2.simulator.accelerator import Accelerator
from dnnweaver2.compiler import *
from dnnweaver2.fpga.fpgamanager import FPGAManager

from dnnweaver2.scalar.dtypes import FixedPoint
import yolo2_tiny as y2t
import sys
np.set_printoptions(threshold=sys.maxsize)
#np.set_printoptions(linewidth=np.inf)

num_rows = 8
num_cols = 8
### Constrtuct a simple graph 

graph = y2t.get_graph()

print('*'*50)
print('List of ops (nodes) in the graph')
# print the ops in the yolo2_graph
for op in graph.op_registry:
    print('\tOp name: {}'.format(op))
print('*'*50)
    
print('*'*50)
print('List of tensors (edges) in the graph')
# print the tensors in the yolo2_graph
#for tname, t in graph.tensor_registry.iteritems():
for tname, t in graph.tensor_registry.items():
    print('\t{}'.format(t))
print('*'*50)


### Set accelerator object 
# on-chip BRAM buffers (number_bram * data_type * entries)
#num_rows = 32
#num_cols = 32
bram = {
    'ibuf':            num_cols * 16 * 2048 / 2,
    'obuf':            num_rows * 64 * 2048 / 2,
    'wbuf': num_cols * num_rows * 16 *  512 / 2,
    'bbuf':            num_rows * 32 * 2048 / 2,
}
acc_obj = Accelerator(
    N=num_rows, M=num_cols,
    prec=16,
    mem_if_width=256,
    frequency=150e6,
    sram=bram
)

print(acc_obj.__str__()) 


### compile and generate the instruction sets for accelerator 
#log_level = logging.DEBUG
log_level = logging.INFO

compiler = GraphCompiler(log_level=log_level)
print('MS :GraphCOmpile Done!!')
inst_binary = compiler.compile(graph=graph, acc_obj=acc_obj)

print('Number of instructions: {}'.format(inst_binary.size))
print(inst_binary)


###
# Program the accelerator
#fpga_manager = FPGAManager()
#fpga_manager.write('pci_cl_data', 0, inst_binary)

#import time

#num_tests = 100
#start = time.time()
#for i in range(num_tests):    
#    # Start the accelerator
#    fpga_manager.start()
#    # Wait for execution to finish
#    fpga_manager.wait_fpga_execution()
#end = time.time()

#print('Frames per second: {}'.format(1./(end-start)))
