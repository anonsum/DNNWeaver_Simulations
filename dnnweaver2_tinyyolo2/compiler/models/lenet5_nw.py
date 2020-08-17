###
### LENET-5 Network model - Refered link:https://engmrk.com/lenet-5-a-classic-cnn-architecture/
###  First run to compile a LENET Network 
import logging
import numpy as np
import array
import math

from dnnweaver2.benchmarks import get_graph
from dnnweaver2.simulator.accelerator import Accelerator
from dnnweaver2.compiler import *
from dnnweaver2.fpga.fpgamanager import FPGAManager

from dnnweaver2.scalar.dtypes import FixedPoint


num_rows = 4
num_cols = 4

### Constrtuct a simple graph 

graph = Graph('LENET-Test: 16-bit', dataset='imagenet', log_level=logging.DEBUG)
batch_size = 1

with graph.as_default():
### Image:(28*28)without Padding
###	 +Conv0(+maxPool): Image:(28*28*1)  K=(1)*(5*5)*(6),  OC=6, s=1 : Output:(28*28)*(6)#pad = 'same'     
###                      : Image:(28*28*6)  K=(2*2),          OC=6, s=2 : Output:(14*14)*(6)
###      +conv1(+maxPool): Image:(14*14*6)  K=(6)*(5*5)*(16) ,OC=16,s=1: Output:(10*10)*(16)#pad = 'same'
###			 : Image:(10*10*16) K=(2*2),          OC=16,s=2: Output:(5*5)*(16)
###      +FC0            : Image:(5*5)*(16)         OC=120   : Output: (1*1)*(120)          #pad = 'same'
###      +FC1		 : Image:(1*1)*(120)        OC = 84  : Output: (1*1)*84	            #pad = 'same'
###      +FC2            : Image:(1*1)*(84)         OC = 10  : Output: (1*1)*10             #pad = 'same'
### 
    with graph.name_scope('inputs'):
        i = get_tensor(shape=(batch_size,28,28,1), name='data', dtype=FQDtype.FXP16, trainable=False) #32*32 after padding
    with graph.name_scope('conv0'):
        weights = get_tensor(shape=(6,5,5,1),
                             name='weights',
                             dtype=FixedPoint(16,12))
        biases = get_tensor(shape=(6),
                             name='biases',
                             dtype=FixedPoint(16,12))
        conv = conv2D(i, weights, biases, pad='SAME', dtype=FixedPoint(16,8))
        pool0 = maxPool(conv, pooling_kernel=(1,2,2,1), stride=(1,2,2,1), pad='VALID')
    
    with graph.name_scope('conv1'):
        weights1 = get_tensor(shape=(16,5,5,6),
                             name='weights1',
                             dtype=FixedPoint(16,12))
        biases1 = get_tensor(shape=(16),
                             name='biases1',
                             dtype=FixedPoint(16,12))
        conv1 = conv2D(pool0, weights1, biases1, pad='SAME', dtype=FixedPoint(16,8))
        pool1 = maxPool(conv1, pooling_kernel=(1,2,2,1), stride=(1,2,2,1), pad='VALID')
  
    with graph.name_scope('fc0'):
        w = pool1.shape[-2]
        h = pool1.shape[-3]
        c = math.ceil(pool1.shape[-1]/num_rows)*num_rows
        size = w * h * c
        in_fc= get_tensor(shape=(1,1,1,size),name='fcin',dtype=FixedPoint(16,8),trainable=False)
        weights2 = get_tensor(shape=(120,1,1,size),
                              name='weights2',
                              dtype=FixedPoint(16,12))
        biases2 = get_tensor(shape=(120),
                              name='biases2',
                              dtype=FixedPoint(16,12))
        fc0 = conv2D(in_fc, weights2, biases2, pad='SAME', dtype=FixedPoint(16,8))

    with graph.name_scope('fc1'):
        cout = fc0.shape[-3]
        hout = fc0.shape[-2]
        wout = math.ceil(fc0.shape[-1]/num_rows)*num_rows 
        size = cout*hout*wout
        in_fc= get_tensor(shape=(1,1,1,size),name='fcin',dtype=FixedPoint(16,8),trainable=False)
        weights3 = get_tensor(shape=(84,1,1, size),
                             name='weights3',
                             dtype=FixedPoint(16,12))
        biases3 = get_tensor(shape=(84),
                             name='biases3',
                             dtype=FixedPoint(16,12))
        fc1 = conv2D(in_fc, weights3, biases3, pad='SAME',dtype=FixedPoint(16,8))
    with graph.name_scope('fc2'):
        cout = fc1.shape[-3]
        hout = fc1.shape[-2]
        wout = math.ceil(fc1.shape[-1]/num_rows)*num_rows
        size = cout*hout*wout
        in_fc= get_tensor(shape=(1,1,1,size),name='fcin',dtype=FixedPoint(16,8),trainable=False) 
        weights4 = get_tensor(shape=(10,1,1, size),
                             name='weights4',
                             dtype=FixedPoint(16,12))
        biases4 = get_tensor(shape=(10),
                             name='biases4',
                             dtype=FixedPoint(16,12))
        fc2 = conv2D(in_fc, weights4, biases4, pad='SAME',dtype=FixedPoint(16,8))
    
print('*'*50)
print('List of ops (nodes) in the graph')
# print the ops 
for op in graph.op_registry:
    print('\tOp name: {}'.format(op))
print('*'*50)
    
print('*'*50)
print('List of tensors (edges) in the graph')
# print the tensors 
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
log_level = logging.DEBUG

compiler = GraphCompiler(log_level=log_level)

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
