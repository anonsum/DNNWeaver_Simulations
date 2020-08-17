###
###  First run to compile a YOLO network 
import logging
import numpy as np
import array
import math
import sys

from dnnweaver2.benchmarks import get_graph
from dnnweaver2.simulator.accelerator import Accelerator
from dnnweaver2.compiler import *
from dnnweaver2.fpga.fpgamanager import FPGAManager

from dnnweaver2.scalar.dtypes import FixedPoint


num_rows = 4
num_cols = 4

graph = Graph('Resnet18-Test: 16-bit', dataset='imagenet', log_level=logging.INFO)
batch_size = 1

with graph.as_default():
### Conv1
    with graph.name_scope('inputs'):
        i = get_tensor(shape=(batch_size,28,28,3), name='data', dtype=FQDtype.FXP16, trainable=False)  
    with graph.name_scope('conv1'):
        weights = get_tensor(shape=(64,7,7,3),
                             name='weights',
                             dtype=FixedPoint(16,12))
        biases = get_tensor(shape=(64),
                             name='biases',
                             dtype=FixedPoint(16,12))
        conv1 = conv2D(i, weights, biases, pad='FULL', stride = (1,2,2,1), dtype=FixedPoint(16,8))
        
        mean = get_tensor(shape = (64),name = 'mean',dtype=FQDtype.FXP16, trainable=False)
        scale = get_tensor(shape = (64),name = 'scale', dtype=FQDtype.FXP16, trainable=False)

        bnout = batch_norm(conv1 , mean , scale , name='bnorm1')
        conv1_relu = leakyReLU(bnout, name='conv1_relu', alpha=0.0, dtype=FixedPoint(16,8)) #ReLu 
        pool1 = maxPool(conv1_relu, pooling_kernel=(1,3,3,1), stride=(1,2,2,1), pad='FULL')

##Conv2_x : Convolution block
## Shrotcut Branch : res2a-branch_1 (to the left) has a short cut with single convolution layer

    with graph.name_scope('res2a_branch1'):
        weights3 = get_tensor(shape=(64,3,3,64),
                             name='weights',
                             dtype=FixedPoint(16,12))
        biases3 = get_tensor(shape=(64),
                             name='biases',
                             dtype=FixedPoint(16,20))
        res2a_branch1 = conv2D(pool1, weights3, biases3, pad='SAME', stride = (1,1,1,1), dtype=FixedPoint(16,8))


### Main Branch : res2a-branch2x (to the right) includes 2 convolution layers   
    with graph.name_scope('res2a_branch2a'):
        weights1 = get_tensor(shape=(64,3,3,64),
                             name='weights',
                             dtype=FixedPoint(16,12))
        biases1 = get_tensor(shape=(64),
                             name='biases',
                             dtype=FixedPoint(16,12))
        res2a_branch2a = conv2D(pool1, weights1, biases1, pad='SAME', stride = (1,1,1,1), dtype=FixedPoint(16,8))
        mean = get_tensor(shape = (64),name = 'mean',dtype=FQDtype.FXP16, trainable=False)
        scale = get_tensor(shape = (64),name = 'scale', dtype=FQDtype.FXP16, trainable=False)

        bnout = batch_norm(res2a_branch2a , mean , scale , name='bnorm1')
        res2a_branch2a_relu = leakyReLU(bnout, name='res2a_branch2a_relu', alpha=0.0, dtype=FixedPoint(16,8)) #ReLu 
          

    with graph.name_scope('res2a_branch2b'):
        weights2 = get_tensor(shape=(64,3,3,64),
                             name='weights',
                             dtype=FixedPoint(16,12))
        biases2 = get_tensor(shape=(64),
                             name='biases',
                             dtype=FixedPoint(16,12))
        res2a_branch2b = conv2D(res2a_branch2a_relu, weights2, biases2, pad='SAME', stride = (1,1,1,1), dtype=FixedPoint(16,8))

       
        #res2a_branch1  : Output of Branch1(Shortcut)
        #res2a_branch2b : Output of Branch2(Main)
        res2a = concat([res2a_branch1,res2a_branch2b], 3, name='concat', dtype=FixedPoint(16,8)) 
    
    
    with graph.name_scope('conv2a'):
       
        mweights1 = get_tensor(shape=(64,1,1,128),
                             name='merged_weights',
                             dtype=FixedPoint(16,12))
        mbiases1 = get_tensor(shape=(64),
                             name='merged_biases',
                             dtype=FixedPoint(16,12))
        conv2a = conv2D(res2a, mweights1, mbiases1, pad="VALID", stride = (1,1,1,1),dtype=FixedPoint(16,8))
        conv2a_relu = leakyReLU(conv2a, name='conv2a_relu', alpha=0.0, dtype=FixedPoint(16,8)) #ReLu 

## Conv2_x Identity Block
## Shortcut branch : Adding a duplicate/dummy convolution block conv2a_dup to the left
    with graph.name_scope('conv2a_dup'):
       
        mweights1 = get_tensor(shape=(64,1,1,128),
                             name='merged_weights',
                             dtype=FixedPoint(16,12))
        mbiases1 = get_tensor(shape=(64),
                             name='merged_biases',
                             dtype=FixedPoint(16,12))
        conv2a_dup = conv2D(res2a, mweights1, mbiases1, pad="VALID", stride = (1,1,1,1),dtype=FixedPoint(16,8))
    
### Main Branch : res2b-branch2x (to the right) includes 2 convolution layers   
    with graph.name_scope('res2b_branch2a'):
        weights1 = get_tensor(shape=(64,3,3,64),
                             name='weights',
                             dtype=FixedPoint(16,12))
        biases1 = get_tensor(shape=(64),
                             name='biases',
                             dtype=FixedPoint(16,12))
        res2b_branch2a = conv2D(conv2a_relu, weights1, biases1, pad='SAME', stride = (1,1,1,1), dtype=FixedPoint(16,8))
        mean = get_tensor(shape = (64),name = 'mean',dtype=FQDtype.FXP16, trainable=False)
        scale = get_tensor(shape = (64),name = 'scale', dtype=FQDtype.FXP16, trainable=False)

        bnout = batch_norm(res2b_branch2a , mean , scale , name='bnorm1')
        res2b_branch2a_relu = leakyReLU(bnout, name='res2b_branch2a_relu', alpha=0.0, dtype=FixedPoint(16,8)) #ReLu 
          

    with graph.name_scope('res2b_branch2b'):
        weights2 = get_tensor(shape=(64,3,3,64),
                             name='weights',
                             dtype=FixedPoint(16,12))
        biases2 = get_tensor(shape=(64),
                             name='biases',
                             dtype=FixedPoint(16,12))
        res2b_branch2b = conv2D(res2b_branch2a_relu, weights2, biases2, pad='SAME', stride = (1,1,1,1), dtype=FixedPoint(16,8)) 

        #conv2a_dup  : Output of Branch1(Shortcut)
        #res2a_branch2b : Output of Branch2(Main)
        res2b = concat([conv2a_dup,res2b_branch2b], 3, name='concat', dtype=FixedPoint(16,8)) 

    
    with graph.name_scope('conv2b'):
       
        mweights1 = get_tensor(shape=(64,1,1,128),
                             name='merged_weights',
                             dtype=FixedPoint(16,12))
        mbiases1 = get_tensor(shape=(64),
                             name='merged_biases',
                             dtype=FixedPoint(16,12))
        conv2b = conv2D(res2b, mweights1, mbiases1, pad="VALID", stride = (1,1,1,1),dtype=FixedPoint(16,8))
        conv2b_relu = leakyReLU(conv2b, name='conv1_relu', alpha=0.0, dtype=FixedPoint(16,8)) #ReLu 

#######################################################################################################################

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
print("BRAM SIZE(bits):",bram)
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
#log_level = logging.INFO

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
