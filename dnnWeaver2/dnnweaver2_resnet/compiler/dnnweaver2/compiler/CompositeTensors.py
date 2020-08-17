from dnnweaver2.tensorOps.cnn import *
from dnnweaver2.graph import Graph
from dnnweaver2.tensor import Tensor

class CompositeBlock(object):
    def __init__(self, ID,nodes_count,node_array):
        self.id = ID
        self.num_nodes = nodes_count
        self.node_array = node_array
        self.block_tensors = []
        return

    def get_block_tensors(self):
        for node in self.node_array:
            op = node.sys_array_op
            pu_ops = node.pu_op
            out_tensors = []
            in_tensors = list(op.input_tensors)
            out_tensors.append(op.output_tensors)
            pu_tensors = []
            for p in pu_ops:
                pu_tensors.append(p.output_tensors)
            comp_tensors = in_tensors + out_tensors + pu_tensors
            self.block_tensors = self.block_tensors + comp_tensors
            in_tensors.clear()
            out_tensors.clear()
            pu_tensors.clear()
            comp_tensors.clear()
        
        return self.block_tensors

class IdentityBlock(CompositeBlock):
    def __init__(self, ID, num_nodes, node_array, concat_node):
        self.node_tensors = {}
        
        self.concat_node = concat_node
        self.concat_address = 0x0000
        self.merging_nodes = []

        #self.block_tensors = []        
        self.rearranged_tensors = []
        self.node_tensors = {}
        super(IdentityBlock, self).__init__(ID=ID,nodes_count=num_nodes,node_array=node_array)

    def add_node_tensors(self, node_tensors):
        self.node_tensors = node_tensors
        return 


    def arrange_tensors(self):
        for node in self.node_array:
            op = node.sys_array_op
            pu_ops = node.pu_op
            out_tensors = []
            in_tensors = list(op.input_tensors)
            out_tensors.append(op.output_tensors)
            pu_tensors = []
            for p in pu_ops:
                pu_tensors.append(p.output_tensors)
            comp_tensors = in_tensors + out_tensors + pu_tensors
            self.block_tensors = self.block_tensors + comp_tensors
            self.node_tensors.update({node:list(comp_tensors)})
            in_tensors.clear()
            out_tensors.clear()
            pu_tensors.clear()
            comp_tensors.clear()
        return self.block_tensors
    '''
    def _rearrange_tensors_in_node(self, node):
        in_tensors = list(node.sys_array_op.input_tensors)
        out_tensors = []
        out_tensors.append(node.sys_array_op.output_tensors)
        pu_tensors = []
        for pu_op in node.pu_op:
            if isinstance(pu_op, TypeCastOp) or isinstance(pu_op, LeakyReLU) or isinstance(pu_op, BatchNorm):
                pu_tensors.insert(0, pu_op.output_tensors)
        tensors = pu_tensors + out_tensors + in_tensors
        self.node_tensors.update({node:list(tensors)})
        self.rearranged_tensors = self.rearranged_tensors + tensors
        return tensors
    '''
    def _find_merging_nodes(self):
        concat_ind = self.node_array.index(self.concat_node) 
        self.merging_nodes.append(self.node_array[concat_ind - 3])
        self.merging_nodes.append(self.node_array[concat_ind - 1])
        return 
 
    def _assign_initial_addr(self):
        for n in self.merging_nodes:
            sys_op_conv = n.sys_array_op
            sys_op_conv.branched = True 
            if len(n.pu_op) >= 1:
               last_pu_op = n.pu_op[-1]
               last_pu_op.output_tensors.fpga_addr = 0x0000
        
    '''
    def _rearrange_nodes_in_block(self):
        concat_ind = self.node_array.index(self.concat_node)
        #swap the two branched nodes in identity block
        temp_node = self.node_array[concat_ind - 1]
        self.node_array[concat_ind - 1] = self.node_array[concat_ind - 2]
        self.node_array[concat_ind - 2] = temp_node      
        #self._rearrange_tensors_in_node(temp_node) 
        return temp_node
    '''
    def rearrange_tensors(self):
        self._find_merging_nodes()
        self._assign_initial_addr()
 
        for node in self.node_array:
            in_tensors = list(node.sys_array_op.input_tensors)
            out_tensors = []
            out_tensors.append(node.sys_array_op.output_tensors)
            pu_tensors = []
            for pu_op in node.pu_op:
                if isinstance(pu_op, TypeCastOp) or isinstance(pu_op, LeakyReLU)or isinstance(pu_op, BatchNorm): 
                   pu_tensors.append(pu_op.output_tensors)
                tensors = in_tensors + out_tensors + pu_tensors
                self.node_tensors.update({node:list(tensors)})
                self.rearranged_tensors = self.rearranged_tensors + tensors
            tensors.clear()
            in_tensors.clear()
            out_tensors.clear()
            pu_tensors.clear()
        return self.rearranged_tensors
               

    def print_nodes(self):
        print("*******************IDENTITY NODES**********************")
        for node in self.node_array:
            print("Node:",node.sys_array_op.name)
     
    def print_tensors(self):
        print("*******************IDENTITY TENSORS**********************")
        for t in self.rearranged_tensors:
            print("tensor:",t.name)

    def assign_concat_address(self):
        self.concat_address = self.concat_node.sys_array_op.output_tensors.fpga_addr 
        for node in self.merging_nodes:
               self.assign_concat_fpga_addr(node)

    def assign_concat_fpga_addr(self,node):
        last_pu_op = node.pu_op[-1]
        last_pu_tensor = last_pu_op.output_tensors
        last_pu_tensor.fpga_addr = self.concat_address #assign same addressa as concat for branched convolution final outputs
        return



class ConvolutionBlock(CompositeBlock):
    def __init__(self, ID, num_nodes, node_array, concat_node=None):
        self.node_tensors = {}
        
        self.concat_node = concat_node
        self.concat_address = 0x0000
        self.merging_nodes = [] #len of this list will always be 2

        #self.block_tensors = []
        self.rearranged_tensors = []
        super(ConvolutionBlock, self).__init__(ID=ID,nodes_count=num_nodes,node_array=node_array)

    def add_node_tensors(self, node_tensors):
        self.node_tensors = node_tensors
        return

    def arrange_tensors(self):
        for node in self.node_array:
            op = node.sys_array_op
            pu_ops = node.pu_op
            out_tensors = []
            in_tensors = list(op.input_tensors)
            out_tensors.append(op.output_tensors)
            pu_tensors = []
            for p in pu_ops:
                pu_tensors.append(p.output_tensors)
            comp_tensors = in_tensors + out_tensors + pu_tensors
            self.block_tensors = self.block_tensors + comp_tensors
            self.node_tensors.update({node:list(comp_tensors)})
            in_tensors.clear()
            out_tensors.clear()
            pu_tensors.clear()
            comp_tensors.clear()
        return self.block_tensors

    def _find_merging_nodes(self):
        concat_ind = self.node_array.index(self.concat_node)
        self.merging_nodes.append(self.node_array[concat_ind - 3])
        self.merging_nodes.append(self.node_array[concat_ind - 1])
        return

    def rearrange_tensors(self):#change name
        self._find_merging_nodes()
        #for node in self.node_array:
            #if isinstance(node.sys_array_op, Convolution) and node.sys_array_op.branched is True:
                #self._assign_initial_addr(node)
        for node in self.merging_nodes:
            self._assign_initial_addr(node)
        
        for node in self.node_array:    
            if self.node_tensors.get(node) is not None:
                self.rearranged_tensors = self.rearranged_tensors + self.node_tensors.get(node)
        return self.rearranged_tensors

    def _assign_initial_addr(self, node):
        last_pu_op = node.pu_op[-1] #assigning address to a tensor of last pu operation of a node to zero
        if isinstance(last_pu_op, TypeCastOp) or isinstance(last_pu_op, LeakyReLU):#?? Batch Norm Needed
           last_pu_tensor = last_pu_op.output_tensors
           last_pu_tensor.fpga_addr = 0x00000
        return

    def assign_concat_address(self):
        #New address allocated for concat, in the same address branched convolution outputs are written in interleaved way
        self.concat_address = self.concat_node.sys_array_op.output_tensors.fpga_addr
        
        for node in self.merging_nodes:
            self.assign_concat_fpga_addr(node)
            sys_op_conv = node.sys_array_op
            sys_op_conv.branched = True 
        return


    def assign_concat_fpga_addr(self,node):
        last_pu_op = node.pu_op[-1]
        last_pu_tensor = last_pu_op.output_tensors
        last_pu_tensor.fpga_addr = self.concat_address #assign same addressa as concat for branched convolution final outputs
        return

    def print_nodes(self):
        print("*******************CONVOLUTION BLOCK NODES**********************")
        for node in self.node_array:
            print("Node:",node.sys_array_op.name)
     
    def print_tensors(self):
        print("*******************CONVOLUTION BLOCK TENSORS**********************")
        for t in self.rearranged_tensors:
            print("tensor:",t.name)

