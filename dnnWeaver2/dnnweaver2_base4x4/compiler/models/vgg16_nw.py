###Build VGG16 Network - Refered Link:https://neurohive.io/en/popular-networks/vgg16/
#Network is different in some other links : https://engmrk.com/vgg16-implementation-using-keras/    
import logging
import numpy as np
import array
import math

from dnnweaver2.benchmarks import get_graph
from dnnweaver2.simulator.accelerator import Accelerator
from dnnweaver2.compiler import *
from dnnweaver2.fpga.fpgamanager import FPGAManager

from dnnweaver2.scalar.dtypes import FixedPoint

num_rows = 32
num_cols = 32


### Constrtuct a simple graph 

graph = Graph('VGG16_Test', dataset='imagenet', log_level=logging.DEBUG)
batch_size = 1

with graph.as_default():
#VGG16 Architecure defined here:
#Image: (224*224)*(3)
#Conv0_0: (224*224)*(3)  : K=(64)*3*3,        stride=1, output:(224*224)*(64)  #pad=2
#Conv0_1: (224*224)*(64) : K=(64)*3*3*(64),   stride=1, output:(224*224)*(64) #pad=2
#maxp0_2: (224*224)*(64):  K= 2*2 ,           stride=2, output:(112*112)*(64)

#Conv1_0: (112*112)*(64)  : K=(128)*3*3*(128), stride=1, output:(112*112)*(128) #pad=2
#Conv1_1: (112*112)*(128) : K=(128)*3*3*(128), stride=1, output:(112*112)*(128) #pad=2
#maxp1_2: (112*112)*(128) : K=2*2 ,            stride=2, output:(56*56)*(128)

#Conv2_0: (56*56)*(128): K=(256)*3*3*(128) , stride=1, output:(56*56)*(256) #pad=2
#Conv2_1: (56*56)*(256): K=(256)*3*3*(256) , stride=1, output:(56*56)*(256) #pad=2
#Conv2_2: (56*56)*(256): K=(256)*3*3*(256) , stride=1, output:(56*56)*(256) #pad=2
#maxp2_3: (56*56)*(256): K= 2*2 ,            stride=2, output:(28*28)*(256)

#Conv3_0: (28*28)*(256): K=(512)*3*3*(256) , stride=1, output:(28*28)*(512) #pad=2
#Conv3_1: (28*28)*(512): K=(512)*3*3*(512) , stride=1, output:(28*28)*(512) #pad=2
#Conv3_2: (28*28)*(512): K=(512)*3*3*(512) , stride=1, output:(28*28)*(512) #pad=2
#maxp3_3: (28*28)*(512): K= 2*2 ,             stride=2, output:(14*14)*(512)

#Conv4_0: (14*14)*(512): K=(512)*3*3*(512),  stride=1, output:(14*14)*(512) #pad=2
#Conv4_1: (14*14)*(512): K=(512)*3*3*(512),  stride=1, output:(14*14)*(512) #pad=2
#Conv4_2: (14*14)*(512): K=(512)*3*3*(512),  stride=1, output:(14*14)*(512) #pad=2
#maxp4_3: (14*14)*(512): K= 2*2,             stride=2, output:(7*7)*(512)

#FC0  : (1*1)*(25088) : K=(4096)*(1*1), stride=0, output:(1*1)*(4096)
#FC1  : (1*1)*(4096)  : K=(4096)*(1*1), stride=0, output:(1*1)*(4096)
#FC2  : (1*1)*(1000)  : K=(1000)*(1*1), stride=0, output:(1*1)*(1000)


    with graph.name_scope('inputs'):
        i = get_tensor(shape=(batch_size,224,224,3), name='data', dtype=FQDtype.FXP16, trainable=False)

    with graph.name_scope('conv0_0'):
        weights0_0 = get_tensor(shape=(64,3,3,3),
                                name='weights0_0',
                                dtype=FixedPoint(16,12))
        biases0_0 = get_tensor(shape=(64),
                             name='biases0_0',
                             dtype=FixedPoint(32,20))
        conv0_0 = conv2D(i, weights0_0, biases0_0, stride=(1,1,1,1), pad='VALID', dtype=FixedPoint(16,8))
    
    with graph.name_scope('conv0_1'):
        weights0_1 = get_tensor(shape=(64,3,3,64),
                             name='weights0_1',
                             dtype=FixedPoint(16,12))
        biases0_1 = get_tensor(shape=(64),
                             name='biases0_1',
                             dtype=FixedPoint(32,20))
        conv0_1 = conv2D(conv0_0, weights0_1, biases0_1, pad='SAME', dtype=FixedPoint(16,8))
        pool0_2 = maxPool(conv0_1, pooling_kernel=(1,2,2,1), stride=(1,2,2,1), pad='VALID')
#+===========================================================================================================
    with graph.name_scope('conv1_0'):
        weights1_0 = get_tensor(shape=(128,3,3,64),
                             name='weights1_0',
                             dtype=FixedPoint(16,12))
        biases1_0 = get_tensor(shape=(128),
                             name='biases1_0',
                             dtype=FixedPoint(32,20))
        conv1_0 = conv2D(pool0_2, weights1_0, biases1_0, pad='SAME', dtype=FixedPoint(16,8))

    with graph.name_scope('conv1_1'):
        weights1_1 = get_tensor(shape=(128,3,3,128),
                             name='weights1_1',
                             dtype=FixedPoint(16,12))
        biases1_1 = get_tensor(shape=(128),
                             name='biases1_1',
                             dtype=FixedPoint(32,20))
        conv1_1 = conv2D(conv1_0, weights1_1, biases1_1, pad='SAME', dtype=FixedPoint(16,8))
        pool1_2 = maxPool(conv1_1, pooling_kernel=(1,2,2,1), stride=(1,2,2,1), pad='VALID')
#============================================================================================================

    with graph.name_scope('conv2_0'):
        weights2_0 = get_tensor(shape=(256,3,3,128),
                             name='weights2_0',
                             dtype=FixedPoint(16,12))
        biases2_0 = get_tensor(shape=(256),
                             name='biases2_0',
                             dtype=FixedPoint(32,20))
        conv2_0 = conv2D(pool1_2, weights2_0, biases2_0, pad='SAME', dtype=FixedPoint(16,8))
    
    with graph.name_scope('conv2_1'):
        weights2_1 = get_tensor(shape=(256,3,3,256),
                             name='weights2_1',
                             dtype=FixedPoint(16,12))
        biases2_1 = get_tensor(shape=(256),
                             name='biases2_1',
                             dtype=FixedPoint(32,20))
        conv2_1 = conv2D(conv2_0, weights2_1, biases2_1, pad='SAME', dtype=FixedPoint(16,8))

    with graph.name_scope('conv2_2'):
        weights2_2 = get_tensor(shape=(256,3,3,256),
                             name='weights2_2',
                             dtype=FixedPoint(16,12))
        biases2_2 = get_tensor(shape=(256),
                             name='biases2_2',
                             dtype=FixedPoint(32,20))
        conv2_2 = conv2D(conv2_1, weights2_2, biases2_2, pad='SAME', dtype=FixedPoint(16,8))
        pool2_3 = maxPool(conv2_2, pooling_kernel=(1,2,2,1), stride=(1,2,2,1), pad='VALID')
#721==============================================================================================================
    with graph.name_scope('conv3_0'):
        weights3_0 = get_tensor(shape=(512,3,3,256),
                             name='weights3_0',
                             dtype=FixedPoint(16,12))
        biases3_0 = get_tensor(shape=(512),
                             name='biases3_0',
                             dtype=FixedPoint(32,20))
        conv3_0 = conv2D(pool2_3, weights3_0, biases3_0, pad='SAME', dtype=FixedPoint(16,8))
    
    with graph.name_scope('conv3_1'):
        weights3_1 = get_tensor(shape=(512,3,3,512),
                             name='weights3_1',
                             dtype=FixedPoint(16,12))
        biases3_1 = get_tensor(shape=(512),
                             name='biases3_1',
                             dtype=FixedPoint(32,20))
        conv3_1 = conv2D(conv3_0, weights3_1, biases3_1, pad='SAME', dtype=FixedPoint(16,8))

    with graph.name_scope('conv3_2'):
        weights3_2 = get_tensor(shape=(512,3,3,512),
                             name='weights3_2',
                             dtype=FixedPoint(16,12))
        biases3_2 = get_tensor(shape=(512),
                             name='biases3_2',
                             dtype=FixedPoint(32,20))
        conv3_2 = conv2D(conv3_1, weights3_2, biases3_2, pad='SAME', dtype=FixedPoint(16,8))
        pool3_3 = maxPool(conv3_2, pooling_kernel=(1,2,2,1), stride=(1,2,2,1), pad='VALID')

#1111==============================================================================================================

    with graph.name_scope('conv4_0'):
        weights4_0 = get_tensor(shape=(512,3,3,512),
                             name='weights4_0',
                             dtype=FixedPoint(16,12))
        biases4_0 = get_tensor(shape=(512),
                             name='biases4_0',
                             dtype=FixedPoint(32,20))
        conv4_0 = conv2D(pool3_3, weights4_0, biases4_0, pad='SAME', dtype=FixedPoint(16,8))
    
    with graph.name_scope('conv4_1'):
        weights4_1 = get_tensor(shape=(512,3,3,512),
                             name='weights4_1',
                             dtype=FixedPoint(16,12))
        biases4_1 = get_tensor(shape=(512),
                             name='biases4_1',
                             dtype=FixedPoint(32,20))
        conv4_1 = conv2D(conv4_0, weights4_1, biases4_1, pad='SAME', dtype=FixedPoint(16,8))

    with graph.name_scope('conv4_2'):
        weights4_2 = get_tensor(shape=(512,3,3,512),
                             name='weights4_2',
                             dtype=FixedPoint(16,12))
        biases4_2 = get_tensor(shape=(512),
                             name='biases4_2',
                             dtype=FixedPoint(32,20))
        conv4_2 = conv2D(conv4_1, weights4_2, biases4_2, pad='SAME', dtype=FixedPoint(16,8))
        pool4_3 = maxPool(conv4_2, pooling_kernel=(1,2,2,1), stride=(1,2,2,1), pad='VALID')
#==============================================================================================================
    
    with graph.name_scope('fc0'):
        cout = pool4_3.shape[-3]
        hout = pool4_3.shape[-2]
        wout = math.ceil(pool4_3.shape[-1]/num_rows)*num_rows
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
