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

num_rows = 32
num_cols = 32

### Constrtuct a simple graph 

graph = y2t.get_graph()
##SS##graph = Graph('YOLOv2-Test: 16-bit', dataset='imagenet', log_level=logging.INFO)
##SS###graph = Graph('YOLOv2-Test: 16-bit', dataset='imagenet', log_level=logging.DEBUG)
##SS##batch_size = 1
##SS##
##SS##with graph.as_default():
##SS##### Conv+conv+FC
##SS##    with graph.name_scope('inputs'):
##SS##        i = get_tensor(shape=(batch_size,8,8,3), name='data', dtype=FQDtype.FXP16, trainable=False)    #8x8 
##SS##    with graph.name_scope('conv0'):
##SS##        #weights = get_tensor(shape=(128, 3, 3, 3),
##SS##        weights = get_tensor(shape=(1,3,3, 3),
##SS##                             name='weights',
##SS##                             dtype=FixedPoint(16,12))
##SS##        #biases = get_tensor(shape=(128),
##SS##        biases = get_tensor(shape=(1),
##SS##                             name='biases',
##SS##                             dtype=FixedPoint(32,20))
##SS##        conv = conv2D(i, weights, biases, pad='SAME', dtype=FixedPoint(16,8))
##SS##        pool = maxPool(conv, pooling_kernel=(1,2,2,1), stride=(1,2,2,1), pad='VALID')
##SS##    with graph.name_scope('conv1'):
##SS##        #weights = get_tensor(shape=(128, 3, 3, 3),
##SS##        weights1 = get_tensor(shape=(1,3,3, 1),
##SS##                             name='weights1',
##SS##                             dtype=FixedPoint(16,12))
##SS##        #biases = get_tensor(shape=(128),
##SS##        biases1 = get_tensor(shape=(1),
##SS##                             name='biases1',
##SS##                             dtype=FixedPoint(32,20))
##SS##        conv1 = conv2D(pool, weights1, biases1, pad='SAME', dtype=FixedPoint(16,8))
##SS##        pool = maxPool(conv1, pooling_kernel=(1,2,2,1), stride=(1,2,2,1), pad='VALID')
##SS##    with graph.name_scope('fc0'):
##SS##        cout = pool.shape[-3]
##SS##        hout = pool.shape[-2]
##SS##        wout = math.ceil(pool.shape[-1]/num_rows)*num_rows
##SS##        size = cout*hout*wout
##SS##        in_fc= get_tensor(shape=(1,1,1,size),name='fcin',dtype=FixedPoint(16,8),trainable=False)    
##SS##        weights1 = get_tensor(shape=(6,1,1, size),
##SS##                             name='weights1',
##SS##                             dtype=FixedPoint(16,12))
##SS##        biases1 = get_tensor(shape=(6),
##SS##                             name='biases1',
##SS##                             dtype=FixedPoint(32,20))
##SS##        fc0 = conv2D(in_fc, weights1, biases1, pad='SAME', dtype=FixedPoint(16,8))
##SS##    with graph.name_scope('fc1'):
##SS##        cout = fc0.shape[-3]
##SS##        hout = fc0.shape[-2]
##SS##        wout = math.ceil(fc0.shape[-1]/num_rows)*num_rows
##SS##        size = cout*hout*wout
##SS##        in_fc= get_tensor(shape=(1,1,1,size),name='fcin',dtype=FixedPoint(16,8),trainable=False)    
##SS##        weights1 = get_tensor(shape=(2,1,1, size),
##SS##                             name='weights1',
##SS##                             dtype=FixedPoint(16,12))
##SS##        biases1 = get_tensor(shape=(2),
##SS##                             name='biases1',
##SS##                             dtype=FixedPoint(32,20))
##SS##        fc1 = conv2D(in_fc, weights1, biases1, pad='SAME', dtype=FixedPoint(16,8))
### MS expt with just FC
##    with graph.name_scope('inputs'):
##        i = get_tensor(shape=(batch_size,1,1,64), name='data', dtype=FQDtype.FXP16, trainable=False)    # 1D Pool 8x8
##    with graph.name_scope('fc0'):
##        weights = get_tensor(shape=(6,1,1, 64),
##                             name='weights',
##                             dtype=FixedPoint(16,12))
##        biases = get_tensor(shape=(6),
##                             name='biases',
##                             dtype=FixedPoint(32,20))
##        fc0 = conv2D(i, weights, biases, pad='SAME', dtype=FixedPoint(16,8))
    
    ### original
    ###   with graph.name_scope('inputs'):
    ###       #i = get_tensor(shape=(batch_size,16,16,3), name='data', dtype=FQDtype.FXP16, trainable=False)    # 16x16
    ###       #i = get_tensor(shape=(batch_size,8,8,3), name='data', dtype=FQDtype.FXP16, trainable=False)    # 16x16
    ###
    ######with graph.name_scope('conv0'):
    ######    #weights = get_tensor(shape=(128, 3, 3, 3),
    ######    weights = get_tensor(shape=(1,3,3, 3),
    ######                         name='weights',
    ######                         dtype=FixedPoint(16,12))
    ######    #biases = get_tensor(shape=(128),
    ######    biases = get_tensor(shape=(1),
    ######                         name='biases',
    ######                         dtype=FixedPoint(32,20))
    ######    conv = conv2D(i, weights, biases, pad='SAME', dtype=FixedPoint(16,8))
    ####### DnnWeaver2 automatically takes care of type conversion
    #######with graph.name_scope('pool1'):
    ######    pool = maxPool(conv, pooling_kernel=(1,2,2,1), stride=(1,2,2,1), pad='VALID')

    ######with graph.name_scope('fc0'):
    ######    weights_fc = get_tensor (shape=(2,4),
    ######                          name = 'weights_fc',
    ######                          dtype = FixedPoint(16,12))
    ######    biases_fc = get_tensor(shape=(2),
    ######                         name='biases_fc',
    ######                         dtype=FixedPoint(32,20))
    ######  #  flattened_1D = flatten(pool1)
    ######    fcout        =matmul(pool,weights_fc,biases_fc)


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
