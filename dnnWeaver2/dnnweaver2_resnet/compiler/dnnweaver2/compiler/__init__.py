from dnnweaver2.tensorOps.cnn import *
from dnnweaver2.graph import Graph
from dnnweaver2.tensor import Tensor

from dnnweaver2.optimizer.optimizer import optimize_for_order, get_stats_fast
from dnnweaver2.isa import *
from dnnweaver2.isa import ScratchPad, AccessType

from collections import OrderedDict, namedtuple
from dnnweaver2.compiler.CompositeTensors import CompositeBlock, IdentityBlock, ConvolutionBlock
import numpy as np

import os
import math

import logging

from dnnweaver2.compiler.pu_compiler import PUCompiler

InstructionBlock = namedtuple('InstructionBlock', ['Op_name', 'Instructions'])
ENABLE_RESNET = 1

class FPGASpec(object):
    def __init__(self, num_ddr=1, size_ddr=2**32, bandwidth_per_ddr=512):
        assert num_ddr > 0
        assert size_ddr > 0
        assert bandwidth_per_ddr > 0
        self.num_ddr = num_ddr
        self.size_ddr = size_ddr
        self.bandwidth_per_ddr = bandwidth_per_ddr

class FPGAMemoryManager(object):
    def __init__(self, fpga_spec=None, log_level=logging.INFO):
        # assert isinstance(fpga_spec, FPGASpec)
        # self.fpga_spec = fpga_spec
        # self.size_ddr = self.fpga_spec.size_ddr
        self.curr_ddr_ptr = 0
        ### MS
        self.prev_ddr_ptr = 0
        self.log = logging.getLogger('FPGA memory manager')
        self.log.setLevel(log_level)

    def alloc_SS(self, tensor, flag):
        assert isinstance(tensor, Tensor)
        if tensor.fpga_addr is None:
           self.log.debug('SS: fpga_shape: {} fpga_size: {}'.format(tensor.fpga_shape, tensor.fpga_size))
           if flag == 1 : #address search for concat layer
               tensor.fpga_addr = self.prev_ddr_ptr
               self.curr_ddr_ptr= self.prev_ddr_ptr
              
               self.log.debug('Assigned address {}:{} to tensor {}'.format((self.curr_ddr_ptr), (self.curr_ddr_ptr+tensor.fpga_size_in_bytes), tensor))
               self.log.debug('SS  tensor {} start address : {} '.format(tensor,hex(tensor.fpga_addr)))
               self.log.debug('*****************************************************')
               
           else:#addressing for other tensors
               tensor.fpga_addr = self.curr_ddr_ptr
           
           self.log.debug('Assigned address {}:{} to tensor {}'.format((self.curr_ddr_ptr), (self.curr_ddr_ptr+tensor.fpga_size_in_bytes), tensor))
           self.log.debug('SS  tensor {} start address : {} '.format(tensor,hex(tensor.fpga_addr)))
           self.log.debug('*****************************************************')
           self.prev_ddr_ptr = self.curr_ddr_ptr
           self.curr_ddr_ptr += int(math.ceil(tensor.fpga_size_in_bytes / 1024) * 1024) + 16
        return
 
    def alloc_MS(self, tensor,flag):
        assert isinstance(tensor, Tensor)
        if tensor.fpga_addr is None:
            if flag == 1 :
                tensor.fpga_addr = self.prev_ddr_ptr
                self.curr_ddr_ptr= self.prev_ddr_ptr
            else :
                tensor.fpga_addr = self.curr_ddr_ptr
            self.log.debug('Tensor {} start address : {} of fpga_shape:{}'.format(tensor,hex(tensor.fpga_addr),tensor.fpga_shape))
            self.log.debug('Assigned start address : {} of fpga_size:{}'.format(hex(tensor.fpga_addr),tensor.fpga_size_in_bytes))
            self.log.debug('*****************************************************')
            self.prev_ddr_ptr = self.curr_ddr_ptr;
            ##SS## Next layer start address compuation set to,
            ##SS## current_layer_start += size required in bytes + 16 bytes. 16bytes extra added
            ##SS## to handle possible overlaps of last layer's end addr and next layer's start addr
            self.curr_ddr_ptr += int(math.ceil(tensor.fpga_size_in_bytes / 1024) * 1024) + 16

    def alloc(self, tensor):
        assert isinstance(tensor, Tensor)
        if tensor.fpga_addr is None:
            tensor.fpga_addr = self.curr_ddr_ptr
            self.log.debug('Assigned address {}:{} to tensor {}'.format(self.curr_ddr_ptr, self.curr_ddr_ptr+tensor.fpga_size_in_bytes, tensor))
            #self.curr_ddr_ptr += 4*int(math.ceil(tensor.fpga_size_in_bytes / 1024.) * 1024) + 1024 * np.random.randint(1, 16)
            self.curr_ddr_ptr += 4*int(math.ceil(tensor.fpga_size_in_bytes / 1024.) * 1024) 

class MacroNode(object):
    def __init__(self, op):
        assert isinstance(op, Convolution) or isinstance(op, Concat)
        self.sys_array_op = op
        self.pu_op = []
        self.name = op.name
    def append(self, op):
        assert isinstance(op, MaxPooling) or isinstance(op, LeakyReLU) or isinstance(op, BatchNorm) or isinstance(op, TypeCastOp) 
#        assert isinstance(op, MaxPooling) or isinstance(op, LeakyReLU) or isinstance(op, BatchNorm) or isinstance(op, TypeCastOp) or isinstance(op, Flatten) or isinstance(op, MatMul)
        #self.log.debug('MS: Appending Node: op:{}'.format(op))
        self.pu_op.append(op)
        self.name = '{}+{}'.format(self.name, op.name)

class GraphCompiler(object):
    layer_num = 0
    layer_name=None  
    total_fpga_bytes = 0.0

    def __init__(self, fpga_spec=None, log_level=logging.INFO):
        self.log = logging.getLogger('Graph Compiler')
        self.log.setLevel(log_level)
        self.fpga_spec = fpga_spec
        if self.fpga_spec is not None:
            assert isinstance(self.fpga_spec, FPGASpec)
            self.fpga_manager = FPGAMemoryManager(self.fpga_spec, log_level=log_level)
        else:
            self.fpga_sepc = FPGASpec()
            self.fpga_manager = FPGAMemoryManager(self.fpga_spec, log_level=log_level)
        self.pu_compiler = PUCompiler(self.fpga_manager, log_level=self.log.level)
        self.conv_tiling = OrderedDict()

    def optimize_tiling(self, op, graph, acc_obj, pool_kernel=None, pool_stride=None,pool_pad=None):
        #self.log.debug("Weights:{} OutputTensors:{} Stride:{} IC:{} OC:{}".format(op.weights.fpga_shape[-2],op.output_tensors.fpga_shape[-2],op.stride[-2],
                                                                                  #op.weights.fpga_shape[-1],op.weights.fpga_shape[-4]))
        K = op.weights.fpga_shape[-2]
        O = op.output_tensors.fpga_shape[-2]
        S = op.stride[-2]#FIX 
        IC = op.weights.fpga_shape[-1]
        OC = op.weights.fpga_shape[-4]
        iprec = 16
        wprec = 16
        B = op.data.fpga_shape[-4]
        im2col = False

        self.log.debug('In optimize_tiling Fn') 
        self.log.debug('KernelSize(K): {} ,OutputSize(O): {},Stride: {},IC: {},OC: {},B: {}'.format(K,O,S,IC,OC,B) ) 
        
        # set energy cost to 0 since this version of the compiler is optimized for performance
        energy_cost = (0,0,0,0,0,0,0,0,0,0)
        conv_params = (acc_obj, K, O, S, IC, OC, B, iprec, wprec, im2col, energy_cost)
        tiling, order, _, _ = optimize_for_order(conv_params, sequential=False, pool_kernel=pool_kernel, pool_stride=pool_stride,pool_pad=pool_pad)
        self.log.debug('Tiling: {} , Order: {} '.format(tiling,order) ) 

        conv_params_with_pool = (acc_obj, K, O, S, IC, OC, B, iprec, wprec, im2col, energy_cost, pool_kernel, pool_stride)

        # Convert tiling and order to an ordered dict
        best_tiling = OrderedDict()
        for o in order:
            best_tiling[o] = tiling[o]

        best_tiling['KH/kh'] = (1, K)
        best_tiling['KW/kw'] = (1, K)
        return best_tiling

    def _alloc_tensor(self, graph):
#        for tname, t in graph.tensor_registry.iteritems():
        self.log.debug ('In _alloc_tensor fn')
        for tname, t in graph.tensor_registry.items():
            self.log.debug ('  tname:{}, t:{}'.format(tname,t))
            if isinstance(t, Tensor):
                #self.fpga_manager.alloc(t)  ##original 
                if tname.split('/')[1] == "fcin" :
                     self.log.debug("FC Layer found")
                     flag =1
                     self.fpga_manager.alloc_MS(t,flag)
                else :
                     flag =0
                     self.fpga_manager.alloc_MS(t,flag)

    def _alloc_tensors(self, tensors):
        for t in tensors:
            flag = 0
            if isinstance(t, Tensor):
                '''
                if 'Concat' in t.name:
                    t.fpga_addr = 0x0000
                    self.log.debug('SS  tensor {} at address : {} '.format(t,hex(t.fpga_addr)))
                    continue
                '''
                if t.name.split('/')[1] == "fcin" :
                     #self.log.debug("FC Layer found")
                     flag =1
                self.fpga_manager.alloc_SS(t,flag)
                
    
    def _dump_addr_header_file(self,graph):
        addrFile = open("param_addr.v","w")
             
        for opname, op in graph.op_registry.items():
            comment = "//In Layer " + opname + "\n"
            addrFile.write(comment)
            if isinstance(op, TypeCastOp) or isinstance(op, MaxPooling) or isinstance(op, LeakyReLU):
               continue
            for t in op.input_tensors:
                if "TypeCastOp" in t.name or "MaxPooling" in t.name or "LeakyReLU" in t.name or "concat" in t.name:
                   continue

                if t.fpga_addr is not  None :
                   sname = str(t.name)
                   sn = sname.replace("/","_")
                   addr = str(hex(t.fpga_addr))
                   line = "parameter " + sn.replace(":","_") + "  " +  "=" + " 32\'h" + addr[2:] + ">>1;\n"
                   addrFile.write(line)
                else:
                   pass
            addrFile.write("\n")
 
            for t in op.input_tensors:
                if "TypeCastOp" in t.name or "MaxPooling" in t.name or "LeakyReLU" in t.name or "concat" in t.name:
                   continue

                if t.fpga_addr is not None:
                   sname = str(t.name)
                   sn = sname.replace("/","_")
                   addr = str(hex(t.fpga_addr))
                   line = "parameter " + sn.replace(":","_") + "_size  " +  "= " + str(t.fpga_size) + ";\n"
                   addrFile.write(line)
                else:
                   pass
            addrFile.write("\n")

            
        for opname, op in graph.op_registry.items():
            comment = "//In Layer " + opname + "\n"
            addrFile.write(comment)
            if isinstance(op, TypeCastOp) or isinstance(op, MaxPooling) or isinstance(op, LeakyReLU):
               continue
            for t in op.input_tensors:
                if "TypeCastOp" in t.name or "MaxPooling" in t.name or "LeakyReLU" in t.name or "Concat" in t.name:
                   continue

                if t.fpga_addr is not None:
                   sname = str(t.name)
                   sn = sname.replace("/","_")
                   addr = str(hex(t.fpga_addr))
                   line = "$readmemh(\"./data/" + sn.replace(":","_") +  ".txt\",ddr_ram," + sn.replace(":","_") + "," + sn.replace(":","_") + "_size"+   "-1);\n"
                   addrFile.write(line)
                else:
                   pass
            addrFile.write("\n")
        addrFile.close()
        return

    def _process_macro_node_array(self, macro_node_array):
        node_array = []
        composite_block_array = []
        unique_block_id = 1
        node_count = 0
        for i in range(len(macro_node_array)):
            macro_node = macro_node_array[i]
            node_count = node_count + 1
            if isinstance(macro_node.sys_array_op, Convolution):
               node_array.append(macro_node)
               continue 

            elif isinstance(macro_node.sys_array_op, Concat):
               node_array.append(macro_node)
               node_array.append(macro_node_array[i+1]) 
                 
            if len(node_array) == 6 and (unique_block_id % 2  == 0):  # Identity Block
               new_block = IdentityBlock(unique_block_id, len(node_array), list(node_array), macro_node)
               self.log.debug("Identity Block created")
            else:  # Convolution blocks
               new_block = ConvolutionBlock(unique_block_id, len(node_array), list(node_array), macro_node)
               self.log.debug("Convolution Block created")
            unique_block_id = unique_block_id + 1
            composite_block_array.append(new_block)
            node_array.clear()

        # Need to handle the next nodes  for the last concat node
        if len(node_array) >0:
           common_block = CompositeBlock(0,len(node_array), list(node_array))
           composite_block_array.append(common_block)
        
        return composite_block_array

    def _process_composite_block_array(self, composite_block_array):

        for i in range(len(composite_block_array)):
            composite_block = composite_block_array[i]
                
            if isinstance(composite_block, ConvolutionBlock):
                composite_block.arrange_tensors()
                tensors = composite_block.rearrange_tensors()
                self._alloc_tensors(tensors)
                composite_block.assign_concat_address()
                #composite_block.print_tensors()

            elif isinstance(composite_block, IdentityBlock):
                tensors = composite_block.rearrange_tensors()
                self._alloc_tensors(tensors)
                composite_block.assign_concat_address()

            elif isinstance(composite_block, CompositeBlock):
                tensors = composite_block.get_block_tensors()
                self._alloc_tensors(tensors)
                
            self.log.debug('*********************NEW ADDRESSING**************************')
            unique_tensors= []
            for t in tensors:
                if isinstance(t, Tensor) and (t not in unique_tensors):
                   unique_tensors.append(t)
            for t in unique_tensors:
                self.log.debug('SS  tensor {} at address : {} '.format(t,hex(t.fpga_addr)))
        return


    def _conv_compile(self, conv_op, pu_op, tiling, array_n, array_m, last=False):
        """
        Compiler for convolution layers
        TODO: replace hard-coded array sizes
        """
        self.log.debug ('MS : In _conv_compile function')
        self.log.debug ('MS : array: {}x{}, last" {} '.format(array_m,array_n,last))
        inst_array = []
        inst_array.append(SetupInstruction(16, 16).get_binary())

        self.log.debug('Convolution op: {}'.format(conv_op.name))

        pool_pad = ((0,0), (0,0), (0,0), (0,0))
        for op in pu_op:
            self.log.debug('PU Op: {}'.format(op.name))
            if isinstance(op, MaxPooling):
                pool_pad = op.pad

        pool_pad_h_t = pool_pad[1][0]
        pool_pad_h_b = pool_pad[1][1]
        pool_pad_w_l = pool_pad[2][0]
        pool_pad_w_r = pool_pad[2][1]
        pool_pad_h = pool_pad_h_t + pool_pad_h_b
        pool_pad_w = pool_pad_w_l + pool_pad_w_r
        

        inst_array.append(BaseAddressInstruction(ScratchPad.IBUF, 0, conv_op.data.fpga_addr).get_binary())
        inst_array.append(BaseAddressInstruction(ScratchPad.WBUF, 0, conv_op.weights.fpga_addr).get_binary())
        inst_array.append(BaseAddressInstruction(ScratchPad.BIAS, 0, conv_op.bias.fpga_addr).get_binary())
        inst_array.append(BaseAddressInstruction(ScratchPad.OBUF, 0, conv_op.output_tensors.fpga_addr).get_binary())

        inst_array.append(BaseAddressInstruction(ScratchPad.IBUF, 1, conv_op.data.fpga_addr).get_binary())
        inst_array.append(BaseAddressInstruction(ScratchPad.WBUF, 1, conv_op.weights.fpga_addr).get_binary())
        inst_array.append(BaseAddressInstruction(ScratchPad.BIAS, 1, conv_op.bias.fpga_addr).get_binary())
        inst_array.append(BaseAddressInstruction(ScratchPad.OBUF, 1, conv_op.output_tensors.fpga_addr).get_binary())

        self.log.debug('Pool_pad_h: {},pool_pad_w: {}'.format(pool_pad_h,pool_pad_w))

        self.log.info('MS : In Layer :{}'.format(conv_op.name))
        self.log.info('MS : Addr -- Data : {} \t Weights : {}'.format(hex(conv_op.data.fpga_addr),hex(conv_op.weights.fpga_addr)))
        self.log.info('MS : Addr -- Bias : {} \t Outputs : {}'.format(hex(conv_op.bias.fpga_addr),hex(conv_op.output_tensors.fpga_addr)))


        # Parallelize loops IC/ic and OC/oc
        tiling['IC/ic'] = (tiling['IC/ic'][0], int(math.ceil(tiling['IC/ic'][1]/float(array_n))))
        tiling['OC/oc'] = (tiling['OC/oc'][0], int(math.ceil(tiling['OC/oc'][1]/float(array_m))))


        b = tiling['B/b'][1]
        ic = tiling['IC/ic'][1]
        oc = tiling['OC/oc'][1]
        oh = tiling['OH/oh'][1]
        ow = tiling['OW/ow'][1]
        kh = tiling['KH/kh'][1]
        kw = tiling['KW/kw'][1]

        inner_loop_tiling = {
                'B/b': b,
                'IC/ic': ic,
                'OC/oc': oc,
                'OH/oh': oh - pool_pad_h,#FIX
                'OW/ow': ow - pool_pad_w,#FIX
                'KH/kh': kh,
                'KW/kw': kw
                }

        outer_loop_strides = {

            'IC/ic': {
                ScratchPad.IBUF: (3, ic),
                ScratchPad.OBUF: (0, 0),
                ScratchPad.WBUF: (3, ic),
                ScratchPad.BIAS: (0, 0),
            },

            'OC/oc': {
                ScratchPad.IBUF: (0, 0),
                ScratchPad.OBUF: (3, oc),
                ScratchPad.WBUF: (0, oc),
                ScratchPad.BIAS: (0, oc),
            },

            'B/b': {
                ScratchPad.IBUF: (0, b),
                ScratchPad.OBUF: (0, 1),
                ScratchPad.WBUF: (0, 0),
                ScratchPad.BIAS: (0, 0),
            },

            'OH/oh': {
                ScratchPad.IBUF: (1, oh),
                ScratchPad.OBUF: (1, oh),
                ScratchPad.WBUF: (0, 0),
                ScratchPad.BIAS: (0, 0),
            },

            'OW/ow': {
                ScratchPad.IBUF: (2, ow),
                ScratchPad.OBUF: (2, ow),
                ScratchPad.WBUF: (0, 0),
                ScratchPad.BIAS: (0, 0),
            },

            'KH/kh': {
                ScratchPad.IBUF: (1, kh),
                ScratchPad.OBUF: (0, 0),
                ScratchPad.WBUF: (1, kh),
                ScratchPad.BIAS: (0, 0),
            },

            'KW/kw': {
                ScratchPad.IBUF: (2, kw),
                ScratchPad.OBUF: (0, 0),
                ScratchPad.WBUF: (2, kw),
                ScratchPad.BIAS: (0, 0),
            }
        }

        tensor_mapping = {
            ScratchPad.IBUF: conv_op.data,
            ScratchPad.OBUF: conv_op.output_tensors, #FIX 
            ScratchPad.WBUF: conv_op.weights,
            ScratchPad.BIAS: conv_op.bias
        }

        tensor_tile_shape = {
            ScratchPad.IBUF: (conv_op.data.fpga_shape[0],
                              conv_op.data.fpga_shape[1],
                              conv_op.data.fpga_shape[2],
                              int(math.ceil(conv_op.data.fpga_shape[3]/float(array_n))),
                              array_n),
            ScratchPad.OBUF: (conv_op.output_tensors.shape[0],#FIX HERE
                              conv_op.output_tensors.shape[1],
                              conv_op.output_tensors.shape[2],
                              int(math.ceil(conv_op.output_tensors.fpga_shape[3]/float(array_n))), array_m),
            ScratchPad.WBUF: (int(math.ceil(conv_op.weights.fpga_shape[0]/float(array_n))),
                              conv_op.weights.fpga_shape[1],
                              conv_op.weights.fpga_shape[2],
                              int(math.ceil(conv_op.weights.fpga_shape[3]/float(array_n))), array_n, array_m),
            ScratchPad.BIAS: (int(math.ceil(conv_op.bias.fpga_shape[0]/float(array_n))),
                              array_n)
        }

        self.log.debug('MS:Before o/p loop processing, array_size:{}'.format(len(inst_array)))
        #outer_loops
        num_outer_loops = 0
#        for l, it in tiling.iteritems():
        for l, it in tiling.items():
            self.log.debug('MS: Tiling Item, l:{}'.format(l))
            self.log.debug('MS: Tiling Item, it:{}'.format(it))
            if it[0] > 1:
                inst_array.append(LoopInstruction(16, 16, it[0]-1).get_binary())
                #for buf, s in outer_loop_strides[l].iteritems():
                for buf, s in outer_loop_strides[l].items():
                    dim, dim_stride = s
                    tensor = tensor_mapping[buf]
                    shape = tensor_tile_shape[buf]
                    if l == 'IC/ic' or l == 'OC/oc':
                        stride = (np.prod(shape[dim+1:]) * dim_stride * tensor.dtype.bits) / 8
                    else:
                        stride = (np.prod(shape[dim+1:]) * conv_op.stride[-2] * dim_stride * tensor.dtype.bits) / 8
                    self.log.debug('MS: Outerloppstrides Item, buf:{},s:{},stride:{},tensor.op:{}'.format(buf,s,stride,tensor.op))
                    if stride >= (1<<16):
                        inst_array.append(GenAddrHighInstruction(buf, AccessType.LD, 16, stride).get_binary())
                    inst_array.append(GenAddrLowInstruction(buf, AccessType.LD, 16, stride).get_binary())
                    #print('MS: Store Instrn. Stride:{}'.format(stride));
                    if tensor.op == conv_op:
                        if stride >= (1<<16):
                            inst_array.append(GenAddrHighInstruction(buf, AccessType.ST, 16, stride).get_binary())
                        inst_array.append(GenAddrLowInstruction(buf, AccessType.ST, 16, stride).get_binary())

                num_outer_loops += 1

        if num_outer_loops == 0:
            inst_array.append(LoopInstruction(16, 16, 0).get_binary())
            self.log.debug('MS:OuterLoop=0.. Called Loop Instruction')
            #for buf, s in outer_loop_strides[l].iteritems():
            for buf, s in outer_loop_strides[l].items():
                tensor = tensor_mapping[buf]
                inst_array.append(GenAddrLowInstruction(buf, AccessType.LD, 16, 0).get_binary())
                if tensor.op == conv_op:
                    inst_array.append(GenAddrLowInstruction(buf, AccessType.ST, 16, 0).get_binary())
            self.log.debug('MS: Num OuterLoop: {} ,array_size: {}'.format(num_outer_loops,len(inst_array)))

        ih = (oh - 1) * conv_op.stride[-3] + kh #FIX
        iw = (ow - 1) * conv_op.stride[-2] + kw #FIX

        # Horizontal stride of kernel over Image Width
        hs =  conv_op.stride[-3]
        # Vertical stride of kernel over Image Height
        vs =  conv_op.stride[-2]

        self.log.debug('MS: (oh,ow):({},{}) conv_op_stride: {}, (ih,iw): ({},{})'.format(oh,ow,conv_op.stride,ih,iw))
        assert pool_pad_h_t == 0
        assert pool_pad_w_l == 0

        padded_tile_shape_mapping = {
            ScratchPad.IBUF: (b,ih,iw,ic),
            ScratchPad.OBUF: (b,oh,ow,oc),
            ScratchPad.WBUF: (oc,kh,kw,ic),
            ScratchPad.BIAS: (oc,)
        }

        #memory_access_loops
#        for buf, tile_shape in padded_tile_shape_mapping.iteritems():
        for buf, tile_shape in padded_tile_shape_mapping.items():
            num_loops = 0
            tensor = tensor_mapping[buf]
            inst_array.append(LDMemInstruction(buf, tensor.dtype.bits//8, buf+1, 1).get_binary())
            if buf == 1:
                inst_array.append(STMemInstruction(buf, tensor.dtype.bits//8, buf+1, 1).get_binary())
            shape = tensor_tile_shape[buf]
            self.log.debug('MS: Shape: {}, tile shape: {},range:{} '.format(shape,tile_shape,range(len(tile_shape)))) 

            for dim in reversed(range(len(tile_shape))):
                s = tile_shape[dim]
                self.log.debug('MS: dim: {} ,s: {}'.format(dim,s))
                if s > 1:
                    stride = (np.prod(shape[dim+1:]) * 1 * tensor.dtype.bits) / 8
                    self.log.debug('MS: Buf: {} ,s:{}  stride:{}'.format(buf,s,stride)) 
                    inst_array.append(LoopInstruction(buf+1, buf+1, s-1).get_binary())
                    if stride >= (1<<16):
                        inst_array.append(GenAddrHighInstruction(buf, AccessType.LD, buf+1, stride).get_binary())
                    inst_array.append(GenAddrLowInstruction(buf, AccessType.LD, buf+1, stride).get_binary())
                    if buf == 1:
                        if stride >= (1<<16):
                            inst_array.append(GenAddrHighInstruction(buf, AccessType.ST, buf+1, stride).get_binary())
                        inst_array.append(GenAddrLowInstruction(buf, AccessType.ST, buf+1, stride).get_binary())
                    num_loops += 1
                self.log.debug('MS: buf:{}, tensor.dtype.bytes:{},array_size:{}'.format(buf,tensor.dtype.bits/8,len(inst_array)))
            if num_loops == 0:
                inst_array.append(LoopInstruction(buf+1, buf+1, 0).get_binary())
                inst_array.append(GenAddrLowInstruction(buf, AccessType.LD, buf+1, 0).get_binary())
                if buf == 1:
                    inst_array.append(GenAddrLowInstruction(buf, AccessType.ST, buf+1, 0).get_binary())
            self.log.debug('MS:array_size:{}'.format(len(inst_array)))
        self.log.debug('MS: Mem Access Loops, NumLoop: {} ,array_size: {}'.format(num_loops,len(inst_array)))

        inner_loop_strides = {
            'IC/ic': {
                ScratchPad.IBUF: (3, 1),
                ScratchPad.OBUF: (0, 0),
                ScratchPad.WBUF: (3, 1),
                ScratchPad.BIAS: (0, 0),
            },
            'OC/oc': {
                ScratchPad.IBUF: (0, 0),
                ScratchPad.OBUF: (3, 1),
                ScratchPad.WBUF: (0, 1),
                ScratchPad.BIAS: (0, 1),
            },
            'B/b': {
                ScratchPad.IBUF: (0, 1),
                ScratchPad.OBUF: (0, 1),
                ScratchPad.WBUF: (0, 0),
                ScratchPad.BIAS: (0, 0),
            },
            'OH/oh': {
                ScratchPad.IBUF: (1, vs),
                ScratchPad.OBUF: (1, 1),
                ScratchPad.WBUF: (0, 0),
                ScratchPad.BIAS: (0, 0),
            },
            'OW/ow': {
                ScratchPad.IBUF: (2, hs),
                ScratchPad.OBUF: (2, 1),
                ScratchPad.WBUF: (0, 0),
                ScratchPad.BIAS: (0, 0),
            },
            'KH/kh': {
                ScratchPad.IBUF: (1, 1),
                ScratchPad.OBUF: (0, 0),
                ScratchPad.WBUF: (1, 1),
                ScratchPad.BIAS: (0, 0),
            },
            'KW/kw': {
                ScratchPad.IBUF: (2, 1),
                ScratchPad.OBUF: (0, 0),
                ScratchPad.WBUF: (2, 1),
                ScratchPad.BIAS: (0, 0),
            }
        }

        inner_loop_order = ('IC/ic', 'KW/kw', 'KH/kh', 'OW/ow', 'OH/oh', 'OC/oc', 'B/b')

        #inner_loops
        self.log.debug("INNER LOOP PROCESSING")
        num_inner_loops = 0
        for l in inner_loop_order:
            it = inner_loop_tiling[l]
            self.log.debug('MS: it:{}'.format(it))
            if it > 1:
                inst_array.append(LoopInstruction(0, 0, it-1).get_binary())
#                for buf, s in inner_loop_strides[l].iteritems():
                for buf, s in inner_loop_strides[l].items():
                    dim, dim_stride = s
                    tensor = tensor_mapping[buf]
                    tile_shape = padded_tile_shape_mapping[buf]
                    stride = np.prod(tile_shape[dim+1:]) * dim_stride
#                    self.log.debug('MS: dim:{}, tile_shape:{} size K: {} ,np_prod:{}, dim_stride :{}'.format(dim,tile_shape,tile_shape[dim+1:],np.prod(tile_shape[dim+1:]),dim_stride))
                    self.log.debug('MS: buf:{},it:{},tile_shape:{},stride{}'.format(buf,it,tile_shape,stride))
                    if stride >= (1<<16):
                        raise ValueError('stride for inner loop is too high: {}'.format(stride))
                        # inst_array.append(GenAddrHighInstruction(buf, AccessType.RD, 0, stride).get_binary())
                    inst_array.append(GenAddrLowInstruction(buf, AccessType.RD, 0, stride).get_binary())
                    if tensor.op == conv_op:
                        inst_array.append(GenAddrLowInstruction(buf, AccessType.WR, 0, stride).get_binary())
                        if stride >= (1<<16):
                            raise ValueError('stride for inner loop is too high: {}'.format(stride))
                            # inst_array.append(GenAddrHighInstruction(buf, AccessType.WR, 0, stride).get_binary())
                num_inner_loops += 1

        if num_inner_loops == 0:
            inst_array.append(LoopInstruction(0, 0, 0).get_binary())
            inst_array.append(GenAddrLowInstruction(ScratchPad.IBUF, AccessType.RD, 0, 0).get_binary())
            inst_array.append(GenAddrLowInstruction(ScratchPad.WBUF, AccessType.RD, 0, 0).get_binary())
            inst_array.append(GenAddrLowInstruction(ScratchPad.OBUF, AccessType.WR, 0, 0).get_binary())
            inst_array.append(GenAddrLowInstruction(ScratchPad.OBUF, AccessType.RD, 0, 0).get_binary())
            inst_array.append(GenAddrLowInstruction(ScratchPad.BIAS, AccessType.RD, 0, 0).get_binary())

        self.log.debug('MS: Before PU operation. Num Inner Loop : {} ,array_size: {}'.format(num_inner_loops,len(inst_array)))
        # PU operations now
        pu_inst = self.pu_compiler.compile_layer(tiling, conv_op, pu_op, simd_lanes=array_m)
        for i in pu_inst:
            inst_array.append(i)
        inst_array.append(BlockEndInstruction(last).get_binary())
        self.log.debug('MS: Last Instrn: {}, Size: {}'.format(inst_array[-1],len(inst_array)))

        return inst_array

    def compile_macro_node(self, graph, acc_obj):
        pass

    def compile(self, graph, acc_obj):

        array_n, array_m = acc_obj.N, acc_obj.M
        assert isinstance(graph, Graph)
        inst_binary = []
        total_ddr_mem_usage = 0.0

        self.log.debug('#'*50)
        self.log.debug('Combining graph ops to create macro op')
        macro_node_array = []
        curr_node = None
      
        for opname, op in graph.op_registry.items():
            self.log.debug('\t{}'.format(opname))
            self.log.debug('MS: opname: {}, op : {}'.format(opname,op))
            if isinstance(op, Convolution) or isinstance(op, Concat):
                if curr_node is None:
                    curr_node = MacroNode(op)
                    self.log.debug('MS: First Node, Conv, New curr node  is : {}'.format(curr_node))
                else:
                    self.log.debug('MS:  op is : {}'.format(op))
                    macro_node_array.append(curr_node)
                    curr_node = MacroNode(op)
            else:
                assert curr_node is not None
                curr_node.append(op)
        assert curr_node is not None
        macro_node_array.append(curr_node)
        self.log.debug('Combining graph ops to create macro op - done!')

        self.log.debug('MS: MacroNodeArray size: {}'.format(len(macro_node_array)))
       
        for i in range(len(macro_node_array)):
            macro_node = macro_node_array[i]
            if isinstance(macro_node.sys_array_op,Concat):
               continue            
            conv_pad = list(macro_node.sys_array_op.pad)

            # We pad the input channels to be a multiple of number of rows
            ic = macro_node.sys_array_op.data.shape[-1]
            ic_padded = int(math.ceil(ic/float(array_n))*array_n)
            ic_padding = ic_padded - ic
            conv_pad[-1] = (0,ic_padding)
            macro_node.sys_array_op.data.fpga_pad = tuple(conv_pad)

            # We pad the output channels to be a multiple of number of columns
            oc = macro_node.sys_array_op.weights.shape[-4]
            oc_padded = int(math.ceil(oc/float(array_m))*array_m)
            oc_padding = oc_padded - oc
            weights_pad = ((0,oc_padding), (0,0), (0,0), (0,ic_padding))

            bias_pad = ((0,oc_padding))
            
            # IC ad OC padding for weights
            self.log.debug("Op:{}".format(macro_node.sys_array_op.name))
            macro_node.sys_array_op.weights.fpga_pad = ((0,oc_padding), (0,0), (0,0), (0, ic_padding))
            self.log.debug("Weights: shape:{} pad:{}".format(macro_node.sys_array_op.weights.fpga_shape,macro_node.sys_array_op.weights.fpga_pad))

            # Padding for convolution output
            conv_out_pad = ((0,0), (0,0), (0,0), (0,oc_padding))
            for op in macro_node.pu_op:
                if isinstance(op, MaxPooling):
                    conv_out_pad = list(op.pad)
                    conv_out_pad[-1] = (conv_out_pad[-1][0], conv_out_pad[-1][1]+ oc_padding)
                    conv_out_pad = tuple(conv_out_pad)
            macro_node.sys_array_op.output_tensors.fpga_pad = conv_out_pad #FIX1 and FIX2
            self.log.debug("ConvOut: shape:{} pad:{}".format(macro_node.sys_array_op.output_tensors.fpga_shape,macro_node.sys_array_op.output_tensors.fpga_pad))
            self.log.debug('ConvInput Data shape:{} Data_pad: {}'.format(macro_node.sys_array_op.data.fpga_shape,macro_node.sys_array_op.data.fpga_pad))
            

            # TODO: verify if this is correct
            #pool_out_pad = ((0,0),(0,0),(0,0),(0,oc_padding))
            #macro_node.pu_op[-1].output_tensors.fpga_pad = pool_out_pad

            self.log.debug('Conv Layer Params. ic={}, ic_padded={}, ic_numpadding: {}'.format(ic,ic_padded,ic_padding))
            self.log.debug('Conv Layer Params. oc={}, oc_padded={}, oc_numpadding: {}'.format(oc,oc_padded,oc_padding))
            self.log.debug('#'*50)

        self.log.debug('#'*50)
        if ENABLE_RESNET:
           carray = self._process_macro_node_array(macro_node_array)
           self._process_composite_block_array(carray)
        
        for i in range(len(macro_node_array)):
            macro_node = macro_node_array[i]
            if isinstance(macro_node.sys_array_op,Concat):
               continue            
            self.log.debug('#'*50)
            self.log.debug('Compiling macro op: {}'.format(macro_node.name))
            self.log.debug('\tConvolution op: {}'.format(macro_node.sys_array_op.name))
            self.log.debug('\tOther ops:')


            for op in macro_node.pu_op:
                self.log.debug('\t\t{}'.format(op.name))

            self.log.debug('Optimizing tiling for Convolution layer {}'.format(macro_node.sys_array_op.name))
            pool_stride = None
            pool_kernel = None
            pool_pad = None
            for op in macro_node.pu_op:
                if isinstance(op, MaxPooling):
                    pool_pad = op.pad
                    pool_stride = op.stride
                    pool_kernel = op.pooling_kernel
                    pool_pad = op.pad #ADDED
                    pool_input = op.data #ADDED
                    self.log.debug('Pool_input:{} pool_pad: {}, pool_stride: {}, pool_kernel:{}'.format(pool_input.shape,pool_pad,pool_stride,pool_kernel))

            #Get the Optimal tiling numbers
            optimal_tiling = self.optimize_tiling(macro_node.sys_array_op, graph, acc_obj, pool_stride=pool_stride, pool_kernel=pool_kernel,pool_pad = pool_pad)
            self.conv_tiling[macro_node.sys_array_op] = optimal_tiling
            indent = 1
            
            for loop, tile in optimal_tiling.items():
                self.log.debug('{}Loop: {:>6}, Tile: {}'.format(indent * '==', loop, tile))
                indent += 1

            last = i == len(macro_node_array) - 1
            self.log.debug('Allocating tensors for macro op: {}'.format(macro_node.name))
            if not ENABLE_RESNET:
               self._alloc_tensor(graph)
            inst_array = self._conv_compile(conv_op=macro_node.sys_array_op, pu_op=macro_node.pu_op, tiling=optimal_tiling, array_n=array_n, array_m=array_m, last=last)
            inst_binary.append(InstructionBlock(macro_node, inst_array))
            self.log.debug('#'*50)

        for tname, t in graph.tensor_registry.items():
            conv_op = macro_node.sys_array_op
            total_ddr_mem_usage += self.ddr_utilization(t,conv_op)
            last_tensor = next(reversed(graph.tensor_registry.keys()))
            if tname == last_tensor:
                with open ("Network_Analysis", "a") as f:
                    f.write("\n# Total fpga_size_bytes:{} B\n".format(self.total_fpga_bytes))
                    f.write("*"*150)
                    f.write("\n")
                    f.write("*"*150)
                    f.write("\nTotal_DDR_size(bytes)      = {} GB".format(FPGASpec().size_ddr/(1024*1024*1024)))
                    f.write("\nTotal_DDR_occupied(bytes)  = {} GB".format(total_ddr_mem_usage/(1024*1024*1024)))
                    f.write("\nAvailable_DDR_memory(bytes)= {} GB".format(((FPGASpec().size_ddr)-(total_ddr_mem_usage))/(1024*1024*1024)))
        self.log.debug('Compiling macro ops - done!')

        inst_array = []
        op_name_array = []
        for i in inst_binary:
            inst = i.Instructions
            op_name = i.Op_name
            self.log.debug('MS:  op_name: {}'.format(op_name))
            for _i in inst:
                inst_array.append(_i)
            # inst_array += inst
####MS
        self.log.debug ('MS: size of instr : {}'.format(len(inst_array)))
        
        with open('instruction.bin', 'w') as f:
            for inst in inst_array:
                f.write('{}'.format(hex(inst)))
                f.write('\n')
       
###            

        with open('inst.bin', 'w') as f:
            for inst in inst_array:
                f.write('{}'.format(inst))
                f.write('\n')
        self._dump_addr_header_file(graph)
        return np.array(inst_array, dtype=np.int32)

    def ddr_utilization(self, t, conv_op):
        tensor_layer_name=t.name.split("/",1)[0]
        tensor_name=t.name.split("/",1)[1]
        if self.layer_num == 0:
            with open ("Network_Analysis","w") as f:
                f.truncate(0) 
                f.write("Tensor_Precision\n")
                f.write("*"*20)
                f.write("\nData_Precision   : {} b".format(conv_op.data.dtype.bits))
                f.write("\nWeight_Precision : {} b".format(conv_op.weights.dtype.bits))
                f.write("\nBias_Precision   : {} b".format(conv_op.bias.dtype.bits))
                f.write("\nOutput_Precision : {} b".format(conv_op.output_tensors.dtype.bits))
                f.write("\n\n")
                f.write("DDR_Configurations\n")
                f.write("*"*20)
                f.write("\nDDR_Size      : {} GB".format((FPGASpec().size_ddr)/(1024*1024*1024)))
                f.write("\nDDR_Datawidth : {} b".format(FPGASpec().bandwidth_per_ddr))
                f.write("\n\n {: <45} {: <25} {: <20} {: <20} {: <25} {: <15}".format("Layer_Name","fpga_shape","fpga_size","fpga_size(bytes)","Address_Range(dec)","Address_Range(hex)"))
                f.write("\n {: <45} {: <25} {: <20} {: <20} {: <25} {: <15}".format("**********","**********","*********","****************","******************","******************"))
                self.layer_num = 1
        
        with open ("Network_Analysis","a") as f:
            
            if tensor_layer_name != self.layer_name:
                self.layer_name = tensor_layer_name
                t_addr_range = int(t.fpga_size_in_bytes + t.fpga_addr)
                t_addr_range_int = str (t.fpga_addr) + ":" + str(t_addr_range) 
                t_addr_range_hex = str (hex(t.fpga_addr)) + ":" + str(hex(t_addr_range))
                f.write("\n# Total fpga_size_bytes:{} B\n".format(self.total_fpga_bytes))
                f.write("\n {: <30}".format(str(self.layer_name)))
                f.write("\n ==> {: <40} {: <30}{: <20}{: <20} {: <25}{: <15}".format(t.name,str(t.fpga_shape),str(t.fpga_size),str( t.fpga_size_in_bytes),str(t_addr_range_int),str(t_addr_range_hex)))
                self.total_fpga_bytes = 0
                     
            else: 
                
                if (t.fpga_addr != None):
                    t_addr_range = int(t.fpga_size_in_bytes + t.fpga_addr)
                    t_addr_range_int = str (t.fpga_addr) + ":" + str(t_addr_range) 
                    t_addr_range_hex = str (hex(t.fpga_addr)) + ":" + str(hex(t_addr_range))
                    f.write("\n ==> {: <40} {: <30}{: <20}{: <20} {: <25}{: <15}".format(t.name,str(t.fpga_shape),str(t.fpga_size),str( t.fpga_size_in_bytes),str(t_addr_range_int),str(t_addr_range_hex)))
                else:
                    f.write("\n ==> {: <41}{: <30}{: <20}{: <20} {: <25}{: <15}".format(t.name,str(t.fpga_shape),str(t.fpga_size),str( t.fpga_size_in_bytes)," "," "))
                    
            self.total_fpga_bytes +=(t.fpga_size_in_bytes)
            return t.fpga_size_in_bytes
            
       
