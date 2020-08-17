###########################################################################
###  LeNet Digit Classification network 
###  Input Image  : 32x32,single channel ( i.e padded 28x28)
###  Kernel Size  : 5x5   
###  Network	  : Conv0-Conv1-fc0-fc1 
###  Network size : 20-50-500-10  
###	qmn       : 9.7 
### 	-  No Batch Norm operation
###     -  Added Relu Layer in between two FC layers(fc0-Relu-fc1)
##########################################################################
import logging
import numpy as np
import array
import math

from dnnweaver2.benchmarks import get_graph
from dnnweaver2.simulator.accelerator import Accelerator
from dnnweaver2.compiler import *
from dnnweaver2.fpga.fpgamanager import FPGAManager

from dnnweaver2.scalar.dtypes import FixedPoint

## systolic array size 
num_rows = 4
num_cols = 4

### graph generation 

graph = Graph('Lenet:20-50-500-10', dataset='mnist', log_level=logging.INFO)
batch_size = 1

with graph.as_default():
    ## 28x28 grey image padded to 32x32  	
    with graph.name_scope('inputs'):
        i = get_tensor(shape=(batch_size,32,32,1), name='data', dtype=FQDtype.FXP16, trainable=False)    #32x32 ( padded image) 
    ## conv0 
    with graph.name_scope('conv0'):
        weights = get_tensor(shape=(20,5,5,1),						## ic=1, oc =20 
                             name='weights',
                             dtype=FixedPoint(16,7))					## q9.7 
        biases = get_tensor(shape=(20),
                             name='biases',
                             dtype=FixedPoint(32,20))
        conv = conv2D(i, weights, biases, pad='VALID', dtype=FixedPoint(16,8))			
        pool = maxPool(conv, pooling_kernel=(1,2,2,1), stride=(1,2,2,1), pad='VALID')
    ## conv1 	
    with graph.name_scope('conv1'):
        weights1 = get_tensor(shape=(50,5,5,20),						##  ic=20, oc =50 
                             name='weights1',
                             dtype=FixedPoint(16,7))
        biases1 = get_tensor(shape=(50),
                             name='biases1',
                             dtype=FixedPoint(32,20))
        conv1 = conv2D(pool, weights1, biases1, pad='VALID', dtype=FixedPoint(16,8))
        pool = maxPool(conv1, pooling_kernel=(1,2,2,1), stride=(1,2,2,1), pad='VALID')
   ## fc0 	
    with graph.name_scope('fc0'):
        cout = pool.shape[-3]
        hout = pool.shape[-2]
        wout = math.ceil(pool.shape[-1]/num_rows)*num_rows
        size = cout*hout*wout
        in_fc= get_tensor(shape=(1,1,1,size),name='fcin',dtype=FixedPoint(16,8),trainable=False)    
        weights1 = get_tensor(shape=(500,1,1, size),				     ##	neurons =500 
                             name='weights1',
                             dtype=FixedPoint(16,7))
        biases1 = get_tensor(shape=(500),
                             name='biases1',
                             dtype=FixedPoint(32,20))
        fc0 = conv2D(in_fc, weights1, biases1, pad='VALID', dtype=FixedPoint(16,8))

    #Relu : Using Leaky_relu API with alpha set to 0.0
    with graph.name_scope('Relu'):
        reluOut = leakyReLU(fc0,name='relu', alpha=0.0, dtype=FixedPoint(16,8))
  
    ## fc1 
    with graph.name_scope('fc1'):
        cout = reluOut.shape[-3]
        hout = reluOut.shape[-2]
        wout = math.ceil(reluOut.shape[-1]/num_rows)*num_rows
        size = cout*hout*wout
        in_fc= get_tensor(shape=(1,1,1,size),name='fcin',dtype=FixedPoint(16,8),trainable=False)    
        weights1 = get_tensor(shape=(10,1,1, size),				     ## neurons =10 	
                             name='weights1',
                             dtype=FixedPoint(16,7))
        biases1 = get_tensor(shape=(10),
                             name='biases1',
                             dtype=FixedPoint(32,20))
        fc1 = conv2D(in_fc, weights1, biases1, pad='VALID', dtype=FixedPoint(16,8))

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
