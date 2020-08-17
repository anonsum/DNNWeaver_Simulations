###Build Alexnet Network - Refered Link:https://www.learnopencv.com/understanding-alexnet/
#                                      :https://medium.com/@smallfishbigsea/a-walk-through-of-alexnet-6cbd137a5637
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

graph = Graph('ALEXNET-Test: 16-bit', dataset='imagenet', log_level=logging.DEBUG)
batch_size = 1

with graph.as_default():
#ALEXNET Architecure defind here:
#Image: (227*227)*(3)
#Conv0: (227*227)*(3): K=(96)*11*11, stride=4, output:(55*55)*(96)
#maxp0: (55*55)*(96) : K=(96)*3*3  , stride=2, output:(27*27)*(96)

#Conv1: (27*27)*(96) : K=(256)*5*5 , stride=1, output:(27*27)*(256) #pad=2
#maxp1: (27*27)*(256): K=(256)*3*3 , stride=2, output:(13*13)*(256)

#Conv2: (13*13)*(256): K=(384)*3*3 , stride=1, output:(13*13)*(384) #pad=1

#Conv3: (13*13)*(384): K=(384)*3*3 , stride=1, output:(13*13)*(384) #pad=1

#Conv4: (13*13)*(384): K=(256)*3*3,  stride=1, output:(13*13)*(256)
#maxp4: (13*13)*(256): K=(256)*(3*3), stride=2, output:(6*6)*(256)

#FC0  : (1*1)*(9216) : K=(4096)*(1*1), stride=0, output:(1*1)*(4096)
#FC1  : (1*1)*(4096) : K=(4096)*(1*1), stride=0, output:(1*1)*(4096)
#FC2  : (1*1)*(4096) : K=(1000)*(1*1), stride=0, output:(1*1)*(1000)
    with graph.name_scope('inputs'):
        i = get_tensor(shape=(batch_size,227,227,3), name='data', dtype=FQDtype.FXP16, trainable=False)

    with graph.name_scope('conv0'):
        weights = get_tensor(shape=(96,11,11,3),
                             name='weights',
                             dtype=FixedPoint(16,12))
        biases = get_tensor(shape=(96),
                             name='biases',
                             dtype=FixedPoint(32,20))
        conv = conv2D(i, weights, biases, stride=(1,4,4,1),pad='VALID', dtype=FixedPoint(16,8))
        pool0 = maxPool(conv, pooling_kernel=(1,3,3,1), stride=(1,2,2,1), pad='VALID')
    
    with graph.name_scope('conv1'):
        weights1 = get_tensor(shape=(256,5,5,96),
                             name='weights1',
                             dtype=FixedPoint(16,12))
        biases1 = get_tensor(shape=(256),
                             name='biases1',
                             dtype=FixedPoint(32,20))
        conv1 = conv2D(pool0, weights1, biases1, pad='SAME', dtype=FixedPoint(16,8))
        pool1 = maxPool(conv1, pooling_kernel=(1,3,3,1), stride=(1,2,2,1), pad='VALID')
    with graph.name_scope('conv2'):
        weights2 = get_tensor(shape=(384,3,3,256),
                             name='weights2',
                             dtype=FixedPoint(16,12))
        biases2 = get_tensor(shape=(384),
                             name='biases2',
                             dtype=FixedPoint(32,20))
        conv2 = conv2D(pool1, weights2, biases2, pad='SAME', dtype=FixedPoint(16,8))
    with graph.name_scope('conv3'):
        weights3 = get_tensor(shape=(384,3,3,384),
                             name='weights3',
                             dtype=FixedPoint(16,12))
        biases3 = get_tensor(shape=(384),
                             name='biases3',
                             dtype=FixedPoint(32,20))
        conv3 = conv2D(conv2, weights3, biases3, pad='SAME', dtype=FixedPoint(16,8))
    with graph.name_scope('conv4'):
        weights4 = get_tensor(shape=(256,3,3,384),
                             name='weights4',
                             dtype=FixedPoint(16,12))
        biases4 = get_tensor(shape=(256),
                             name='biases4',
                             dtype=FixedPoint(32,20))
        conv4 = conv2D(conv3, weights4, biases4, pad='SAME', dtype=FixedPoint(16,8))
        pool4 = maxPool(conv4, pooling_kernel=(1,3,3,1), stride=(1,2,2,1), pad='VALID')
    with graph.name_scope('fc0'):
        cout = pool4.shape[-3]
        hout = pool4.shape[-2]
        wout = math.ceil(pool4.shape[-1]/num_rows)*num_rows
        size = cout*hout*wout
        in_fc= get_tensor(shape=(1,1,1,size),name='fcin',dtype=FixedPoint(16,8),trainable=False)    
        weights5 = get_tensor(shape=(4096,1,1, size),
                             name='weights5',
                             dtype=FixedPoint(16,12))
        biases5 = get_tensor(shape=(4096),
                             name='biases5',
                             dtype=FixedPoint(32,20))
        fc0 = conv2D(in_fc, weights5, biases5, pad='SAME',dtype=FixedPoint(16,8))
    with graph.name_scope('fc1'):
        cout = fc0.shape[-3]
        hout = fc0.shape[-2]
        wout = math.ceil(fc0.shape[-1]/num_rows)*num_rows
        size = cout*hout*wout
        in_fc= get_tensor(shape=(1,1,1,size),name='fcin',dtype=FixedPoint(16,8),trainable=False)    
        weights6 = get_tensor(shape=(4096,1,1, size),
                             name='weights6',
                             dtype=FixedPoint(16,12))
        biases6 = get_tensor(shape=(4096),
                             name='biases6',
                             dtype=FixedPoint(32,20))
        fc1 = conv2D(in_fc, weights6, biases6, pad='SAME',dtype=FixedPoint(16,8))
    with graph.name_scope('fc2'):
        cout = fc1.shape[-3]
        hout = fc1.shape[-2]
        wout = math.ceil(fc1.shape[-1]/num_rows)*num_rows
        size = cout*hout*wout
        in_fc= get_tensor(shape=(1,1,1,size),name='fcin',dtype=FixedPoint(16,8),trainable=False)    
        weights7 = get_tensor(shape=(1000,1,1, size),
                             name='weights7',
                             dtype=FixedPoint(16,12))
        biases7 = get_tensor(shape=(1000),
                             name='biases7',
                             dtype=FixedPoint(32,20))
        fc2 = conv2D(in_fc, weights7, biases7, pad='SAME',dtype=FixedPoint(16,8))

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
