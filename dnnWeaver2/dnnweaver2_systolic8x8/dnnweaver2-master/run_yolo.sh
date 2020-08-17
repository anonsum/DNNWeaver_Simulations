DEBUG:YOLOv2-Test: 16-bit:Created tensor inputs/data[1,416,416,3] (FXP16 (8,8))
DEBUG:YOLOv2-Test: 16-bit:Created tensor conv0/weights[1,3,3,3] (FXP16 (4,12))
DEBUG:YOLOv2-Test: 16-bit:Created tensor conv0/biases[1] (FXP32 (12,20))
DEBUG:YOLOv2-Test: 16-bit:Created tensor conv0/Convolution[1,416,416,1] (FXP64 (44,20))
DEBUG:YOLOv2-Test: 16-bit:Created op conv0/Convolution
DEBUG:YOLOv2-Test: 16-bit:Created tensor conv0/TypeCastOp[1,416,416,1] (FXP16 (8,8))
DEBUG:YOLOv2-Test: 16-bit:Created op conv0/TypeCastOp
DEBUG:Graph Compiler:##################################################
DEBUG:Graph Compiler:Combining graph ops to create macro op
DEBUG:Graph Compiler:	conv0/Convolution
DEBUG:Graph Compiler:MS: opname: conv0/Convolution, op : <dnnweaver2.tensorOps.cnn.Convolution object at 0x7ff94f2768d0>
DEBUG:Graph Compiler:MS: First Node, Conv, New curr node  is : <dnnweaver2.compiler.MacroNode object at 0x7ff94f276be0>
DEBUG:Graph Compiler:	conv0/TypeCastOp
DEBUG:Graph Compiler:MS: opname: conv0/TypeCastOp, op : <dnnweaver2.tensorOps.cnn.TypeCastOp object at 0x7ff94f2769e8>
DEBUG:Graph Compiler:Combining graph ops to create macro op - done!
DEBUG:Graph Compiler:MS: MacroNodeArray size: 1
DEBUG:Graph Compiler:MS: Cov Layer Params. ic=3, ic_padded=4, ic_numpadding: 1
DEBUG:Graph Compiler:MS: Cov Layer Params. oc=1, oc_padded=4, oc_numpadding: 3
DEBUG:Graph Compiler:MS: Cov Layer Params. Weights_pad =((0, 3), (0, 0), (0, 0), (0, 1)), bias_pad=(0, 3)
DEBUG:Graph Compiler:MS: Cov Layer Params. Input Data_pad: [(0, 0), (1, 1), (1, 1), (0, 1)] Weights_pad :((0, 0), (1, 1), (1, 1), (0, 1)), conv out pad : ((0, 3), (0, 0), (0, 0), (0, 1))
DEBUG:Graph Compiler:##################################################
DEBUG:Graph Compiler:##################################################
DEBUG:Graph Compiler:Compiling macro op: conv0/Convolution+conv0/TypeCastOp
DEBUG:Graph Compiler:	Convolution op: conv0/Convolution
DEBUG:Graph Compiler:	Other ops:
DEBUG:Graph Compiler:		conv0/TypeCastOp
DEBUG:Graph Compiler:Optimizing tiling for Convolution layer conv0/Convolution
DEBUG:Graph Compiler:MS : In optimize_tiling Fn
DEBUG:Graph Compiler:MS : KernelSize(K): 3 , OutputSize(O) : 416 , OutputStride: 1
DEBUG:Graph Compiler:MS : IC: 4 , OC: 4 , B: 1
**************************************************
List of ops (nodes) in the graph
	Op name: conv0/Convolution
	Op name: conv0/TypeCastOp
**************************************************
**************************************************
List of tensors (edges) in the graph
	inputs/data[1,416,416,3] (FXP16 (8,8))
	conv0/weights[1,3,3,3] (FXP16 (4,12))
	conv0/biases[1] (FXP32 (12,20))
	conv0/Convolution[1,416,416,1] (FXP64 (44,20))
	conv0/TypeCastOp[1,416,416,1] (FXP16 (8,8))
**************************************************
Accelerator object
	Precision: 16
	Systolic array size: 4 -rows x 4 -columns
	IBUF size:    8,192.0 Bytes
	WBUF size:    8,192.0 Bytes
	OBUF size:   32,768.0 Bytes
	BBUF size:   16,384.0 Bytes
Double buffering enabled. Sizes of SRAM are halved
DEBUG:Graph Compiler:MS : tiling: {'B/b': (1, 1), 'OW/ow': (26, 16), 'OH/oh': (26, 16), 'IC/ic': (1, 4), 'OC/oc': (1, 4)} , order: ('OH/oh', 'B/b', 'OW/ow', 'IC/ic', 'OC/oc') 
DEBUG:Graph Compiler:Optimal tiling and ordering:
DEBUG:Graph Compiler:==Loop:  OH/oh, Tile: (26, 16)
DEBUG:Graph Compiler:====Loop:    B/b, Tile: (1, 1)
DEBUG:Graph Compiler:======Loop:  OW/ow, Tile: (26, 16)
DEBUG:Graph Compiler:========Loop:  IC/ic, Tile: (1, 4)
DEBUG:Graph Compiler:==========Loop:  OC/oc, Tile: (1, 4)
DEBUG:Graph Compiler:============Loop:  KH/kh, Tile: (1, 3)
DEBUG:Graph Compiler:==============Loop:  KW/kw, Tile: (1, 3)
DEBUG:Graph Compiler:Allocating tensors for macro op: conv0/Convolution+conv0/TypeCastOp
DEBUG:FPGA memory manager:Assigned address 0:1397792.0 to tensor inputs/data[1,416,416,3] (FXP16 (8,8))
DEBUG:FPGA memory manager:Assigned address 5607424:5607712.0 to tensor conv0/weights[1,3,3,3] (FXP16 (4,12))
DEBUG:FPGA memory manager:Assigned address 5623808:5623812.0 to tensor conv0/biases[1] (FXP32 (12,20))
DEBUG:FPGA memory manager:Assigned address 5642240:11180032.0 to tensor conv0/Convolution[1,416,416,1] (FXP64 (44,20))
DEBUG:FPGA memory manager:Assigned address 27794432:29178880.0 to tensor conv0/TypeCastOp[1,416,416,1] (FXP16 (8,8))
DEBUG:Graph Compiler:MS : In _conv_compile function
DEBUG:Graph Compiler:MS : array: 4x4, last" True 
DEBUG:Graph Compiler:Convolution op: conv0/Convolution
DEBUG:Graph Compiler:PU Op: conv0/TypeCastOp
DEBUG:Graph Compiler:MS : Pool_pad_h_t: 0, pool_pad_h_b: 0
DEBUG:Graph Compiler:MS : Pool_pad_w_l: 0, pool_pad_w_r: 0
DEBUG:Graph Compiler:MS : Pool_pad_h: 0,pool_pad_w: 0
DEBUG:Graph Compiler:MS:  BaseAddress  array_size: 9, value: 2434793474
DEBUG:Graph Compiler:MS : IC/ic: (1, 1), OC/oc: (1, 1) 
DEBUG:Graph Compiler:MS:Before o/p loop processing, array_size:9
DEBUG:Graph Compiler:MS: Tiling Item, l:OH/oh
DEBUG:Graph Compiler:MS: Tiling Item, it:(26, 16)
DEBUG:Graph Compiler:MS: Outerloppstrides Item, buf:0,s:(1, 16),stride:53504.0,tensor.op:None
DEBUG:Graph Compiler:MS: Outerloppstrides Item, buf:1,s:(1, 16),stride:212992.0,tensor.op:<dnnweaver2.tensorOps.cnn.Convolution object at 0x7ff94f2768d0>
DEBUG:Graph Compiler:MS: Outerloppstrides Item, buf:2,s:(0, 0),stride:0.0,tensor.op:None
DEBUG:Graph Compiler:MS: Outerloppstrides Item, buf:3,s:(0, 0),stride:0.0,tensor.op:None
DEBUG:Graph Compiler:MS: Tiling Item, l:B/b
DEBUG:Graph Compiler:MS: Tiling Item, it:(1, 1)
DEBUG:Graph Compiler:MS: Tiling Item, l:OW/ow
DEBUG:Graph Compiler:MS: Tiling Item, it:(26, 16)
DEBUG:Graph Compiler:MS: Outerloppstrides Item, buf:0,s:(2, 16),stride:128.0,tensor.op:None
DEBUG:Graph Compiler:MS: Outerloppstrides Item, buf:1,s:(2, 16),stride:512.0,tensor.op:<dnnweaver2.tensorOps.cnn.Convolution object at 0x7ff94f2768d0>
DEBUG:Graph Compiler:MS: Outerloppstrides Item, buf:2,s:(0, 0),stride:0.0,tensor.op:None
DEBUG:Graph Compiler:MS: Outerloppstrides Item, buf:3,s:(0, 0),stride:0.0,tensor.op:None
DEBUG:Graph Compiler:MS: Tiling Item, l:IC/ic
DEBUG:Graph Compiler:MS: Tiling Item, it:(1, 1)
DEBUG:Graph Compiler:MS: Tiling Item, l:OC/oc
DEBUG:Graph Compiler:MS: Tiling Item, it:(1, 1)
DEBUG:Graph Compiler:MS: Tiling Item, l:KH/kh
DEBUG:Graph Compiler:MS: Tiling Item, it:(1, 3)
DEBUG:Graph Compiler:MS: Tiling Item, l:KW/kw
DEBUG:Graph Compiler:MS: Tiling Item, it:(1, 3)
DEBUG:Graph Compiler:MS: (oh,ow):(16,16) conv_op_stride: (1, 1, 1, 1), (ih,iw): (18,18)
DEBUG:Graph Compiler:MS: Shape: (1, 418, 418, 1, 4), len: <range_iterator object at 0x7ff94f2a0ab0> 
DEBUG:Graph Compiler:MS: buf:0, tensor.dtype.bytes:2.0,array_size:24
DEBUG:Graph Compiler:MS: Buf: 0 ,s:18  stride:8.0
DEBUG:Graph Compiler:MS: buf:0, tensor.dtype.bytes:2.0,array_size:26
DEBUG:Graph Compiler:MS: Buf: 0 ,s:18  stride:3344.0
DEBUG:Graph Compiler:MS: buf:0, tensor.dtype.bytes:2.0,array_size:28
DEBUG:Graph Compiler:MS: buf:0, tensor.dtype.bytes:2.0,array_size:28
DEBUG:Graph Compiler:MS:array_size:28
DEBUG:Graph Compiler:MS: Shape: (1, 416, 416, 1, 4), len: <range_iterator object at 0x7ff94f2a0ab0> 
DEBUG:Graph Compiler:MS: buf:1, tensor.dtype.bytes:8.0,array_size:30
DEBUG:Graph Compiler:MS: Buf: 1 ,s:16  stride:32.0
DEBUG:Graph Compiler:MS: buf:1, tensor.dtype.bytes:8.0,array_size:33
DEBUG:Graph Compiler:MS: Buf: 1 ,s:16  stride:13312.0
DEBUG:Graph Compiler:MS: buf:1, tensor.dtype.bytes:8.0,array_size:36
DEBUG:Graph Compiler:MS: buf:1, tensor.dtype.bytes:8.0,array_size:36
DEBUG:Graph Compiler:MS:array_size:36
DEBUG:Graph Compiler:MS: Shape: (1, 3, 3, 1, 4, 4), len: <range_iterator object at 0x7ff94f2a0ab0> 
DEBUG:Graph Compiler:MS: buf:2, tensor.dtype.bytes:2.0,array_size:37
DEBUG:Graph Compiler:MS: Buf: 2 ,s:3  stride:32.0
DEBUG:Graph Compiler:MS: buf:2, tensor.dtype.bytes:2.0,array_size:39
DEBUG:Graph Compiler:MS: Buf: 2 ,s:3  stride:96.0
DEBUG:Graph Compiler:MS: buf:2, tensor.dtype.bytes:2.0,array_size:41
DEBUG:Graph Compiler:MS: buf:2, tensor.dtype.bytes:2.0,array_size:41
DEBUG:Graph Compiler:MS:array_size:41
DEBUG:Graph Compiler:MS: Shape: (1, 4), len: <range_iterator object at 0x7ff94f2a0ab0> 
DEBUG:Graph Compiler:MS: buf:3, tensor.dtype.bytes:4.0,array_size:42
DEBUG:Graph Compiler:MS:array_size:44
DEBUG:Graph Compiler:MS: Mem Access Loops, NumLoop: 0 ,array_size: 44
DEBUG:Graph Compiler:MS: it:1
DEBUG:Graph Compiler:MS: it:3
DEBUG:Graph Compiler:MS: buf:0,it:3,tile_shape:(1, 18, 18, 1),stride1
DEBUG:Graph Compiler:MS: buf:1,it:3,tile_shape:(1, 16, 16, 1),stride0
DEBUG:Graph Compiler:MS: buf:2,it:3,tile_shape:(1, 3, 3, 1),stride1
DEBUG:Graph Compiler:MS: buf:3,it:3,tile_shape:(1,),stride0.0
DEBUG:Graph Compiler:MS: it:3
DEBUG:Graph Compiler:MS: buf:0,it:3,tile_shape:(1, 18, 18, 1),stride18
DEBUG:Graph Compiler:MS: buf:1,it:3,tile_shape:(1, 16, 16, 1),stride0
DEBUG:Graph Compiler:MS: buf:2,it:3,tile_shape:(1, 3, 3, 1),stride3
DEBUG:Graph Compiler:MS: buf:3,it:3,tile_shape:(1,),stride0.0
DEBUG:Graph Compiler:MS: it:16
DEBUG:Graph Compiler:MS: buf:0,it:16,tile_shape:(1, 18, 18, 1),stride1
DEBUG:Graph Compiler:MS: buf:1,it:16,tile_shape:(1, 16, 16, 1),stride1
DEBUG:Graph Compiler:MS: buf:2,it:16,tile_shape:(1, 3, 3, 1),stride0
DEBUG:Graph Compiler:MS: buf:3,it:16,tile_shape:(1,),stride0.0
DEBUG:Graph Compiler:MS: it:16
DEBUG:Graph Compiler:MS: buf:0,it:16,tile_shape:(1, 18, 18, 1),stride18
DEBUG:Graph Compiler:MS: buf:1,it:16,tile_shape:(1, 16, 16, 1),stride16
DEBUG:Graph Compiler:MS: buf:2,it:16,tile_shape:(1, 3, 3, 1),stride0
DEBUG:Graph Compiler:MS: buf:3,it:16,tile_shape:(1,),stride0.0
DEBUG:Graph Compiler:MS: it:1
DEBUG:Graph Compiler:MS: it:1
DEBUG:Graph Compiler:MS: Before PU operation. Num Inner Loop : 4 ,array_size: 68
DEBUG:Graph Compiler:MS: Last Instrn: 2147483649, Size: 107
DEBUG:Graph Compiler:##################################################
DEBUG:Graph Compiler:Compiling macro ops - done!
DEBUG:Graph Compiler:MS:  op_name: <dnnweaver2.compiler.MacroNode object at 0x7ff94f276be0>
DEBUG:Graph Compiler:MS: size of instr : 107
MS: opcode:0x0, op_spec: 0x24, loopid:0x0, imm:0, Instr: 0x4800000
MS: opcode:0x9, op_spec: 0x0, loopid:0x0, imm:0, Instr: 0x90000000
MS: opcode:0x9, op_spec: 0x10, loopid:0x15, imm:36864, Instr: 0x92159000
MS: opcode:0x9, op_spec: 0x18, loopid:0x15, imm:53248, Instr: 0x9315d000
MS: opcode:0x9, op_spec: 0x8, loopid:0x16, imm:6144, Instr: 0x91161800
MS: opcode:0x9, op_spec: 0x1, loopid:0x0, imm:0, Instr: 0x90200000
MS: opcode:0x9, op_spec: 0x11, loopid:0x0, imm:2, Instr: 0x92200002
MS: opcode:0x9, op_spec: 0x19, loopid:0x0, imm:2, Instr: 0x93200002
MS: opcode:0x9, op_spec: 0x9, loopid:0x0, imm:2, Instr: 0x91200002
MS : Addr -- Data : 0x0 	 Weights : 0x559000
MS : Addr -- Bias : 0x55d000 	 Outputs : 0x561800
MS: b: 1, ic: 1, oc: 1, oh: 16, ow: 16, kh: 3,kw:3
MS: opcode:0x7, op_spec: 0x10, loopid:0x10, imm:25, Instr: 0x72100019
MS: opcode:0x6, op_spec: 0x0, loopid:0x10, imm:53504, Instr: 0x6010d100
MS: Store Instrn. Stride:53504.0
MS: opcode:0x5, op_spec: 0x8, loopid:0x10, imm:3, Instr: 0x51100003
MS: opcode:0x6, op_spec: 0x8, loopid:0x10, imm:16384, Instr: 0x61104000
MS: Store Instrn. Stride:212992.0
MS: opcode:0x5, op_spec: 0x9, loopid:0x10, imm:3, Instr: 0x51300003
MS: opcode:0x6, op_spec: 0x9, loopid:0x10, imm:16384, Instr: 0x61304000
MS: opcode:0x6, op_spec: 0x10, loopid:0x10, imm:0, Instr: 0x62100000
MS: Store Instrn. Stride:0.0
MS: opcode:0x6, op_spec: 0x18, loopid:0x10, imm:0, Instr: 0x63100000
MS: Store Instrn. Stride:0.0
MS: opcode:0x7, op_spec: 0x10, loopid:0x10, imm:25, Instr: 0x72100019
MS: opcode:0x6, op_spec: 0x0, loopid:0x10, imm:128, Instr: 0x60100080
MS: Store Instrn. Stride:128.0
MS: opcode:0x6, op_spec: 0x8, loopid:0x10, imm:512, Instr: 0x61100200
MS: Store Instrn. Stride:512.0
MS: opcode:0x6, op_spec: 0x9, loopid:0x10, imm:512, Instr: 0x61300200
MS: opcode:0x6, op_spec: 0x10, loopid:0x10, imm:0, Instr: 0x62100000
MS: Store Instrn. Stride:0.0
MS: opcode:0x6, op_spec: 0x18, loopid:0x10, imm:0, Instr: 0x63100000
MS: Store Instrn. Stride:0.0
MS: opcode:0x1, op_spec: 0x1, loopid:0x1, imm:1, Instr: 0x10210001
MS: opcode:0x7, op_spec: 0x1, loopid:0x1, imm:17, Instr: 0x70210011
MS: opcode:0x6, op_spec: 0x0, loopid:0x1, imm:8, Instr: 0x60010008
MS: opcode:0x7, op_spec: 0x1, loopid:0x1, imm:17, Instr: 0x70210011
MS: opcode:0x6, op_spec: 0x0, loopid:0x1, imm:3344, Instr: 0x60010d10
MS: opcode:0x1, op_spec: 0xb, loopid:0x2, imm:1, Instr: 0x11620001
MS: opcode:0x2, op_spec: 0xb, loopid:0x2, imm:1, Instr: 0x21620001
MS: opcode:0x7, op_spec: 0x2, loopid:0x2, imm:15, Instr: 0x7042000f
MS: opcode:0x6, op_spec: 0x8, loopid:0x2, imm:32, Instr: 0x61020020
MS: opcode:0x6, op_spec: 0x9, loopid:0x2, imm:32, Instr: 0x61220020
MS: opcode:0x7, op_spec: 0x2, loopid:0x2, imm:15, Instr: 0x7042000f
MS: opcode:0x6, op_spec: 0x8, loopid:0x2, imm:13312, Instr: 0x61023400
MS: opcode:0x6, op_spec: 0x9, loopid:0x2, imm:13312, Instr: 0x61223400
MS: opcode:0x1, op_spec: 0x11, loopid:0x3, imm:1, Instr: 0x12230001
MS: opcode:0x7, op_spec: 0x3, loopid:0x3, imm:2, Instr: 0x70630002
MS: opcode:0x6, op_spec: 0x10, loopid:0x3, imm:32, Instr: 0x62030020
MS: opcode:0x7, op_spec: 0x3, loopid:0x3, imm:2, Instr: 0x70630002
MS: opcode:0x6, op_spec: 0x10, loopid:0x3, imm:96, Instr: 0x62030060
MS: opcode:0x1, op_spec: 0x1a, loopid:0x4, imm:1, Instr: 0x13440001
MS: opcode:0x7, op_spec: 0x4, loopid:0x4, imm:0, Instr: 0x70840000
MS: opcode:0x6, op_spec: 0x18, loopid:0x4, imm:0, Instr: 0x63040000
MS: opcode:0x7, op_spec: 0x0, loopid:0x0, imm:2, Instr: 0x70000002
MS: opcode:0x6, op_spec: 0x2, loopid:0x0, imm:1, Instr: 0x60400001
MS: opcode:0x6, op_spec: 0xa, loopid:0x0, imm:0, Instr: 0x61400000
MS: opcode:0x6, op_spec: 0xb, loopid:0x0, imm:0, Instr: 0x61600000
MS: opcode:0x6, op_spec: 0x12, loopid:0x0, imm:1, Instr: 0x62400001
MS: opcode:0x6, op_spec: 0x1a, loopid:0x0, imm:0, Instr: 0x63400000
MS: opcode:0x7, op_spec: 0x0, loopid:0x0, imm:2, Instr: 0x70000002
MS: opcode:0x6, op_spec: 0x2, loopid:0x0, imm:18, Instr: 0x60400012
MS: opcode:0x6, op_spec: 0xa, loopid:0x0, imm:0, Instr: 0x61400000
MS: opcode:0x6, op_spec: 0xb, loopid:0x0, imm:0, Instr: 0x61600000
MS: opcode:0x6, op_spec: 0x12, loopid:0x0, imm:3, Instr: 0x62400003
MS: opcode:0x6, op_spec: 0x1a, loopid:0x0, imm:0, Instr: 0x63400000
MS: opcode:0x7, op_spec: 0x0, loopid:0x0, imm:15, Instr: 0x7000000f
MS: opcode:0x6, op_spec: 0x2, loopid:0x0, imm:1, Instr: 0x60400001
MS: opcode:0x6, op_spec: 0xa, loopid:0x0, imm:1, Instr: 0x61400001
MS: opcode:0x6, op_spec: 0xb, loopid:0x0, imm:1, Instr: 0x61600001
MS: opcode:0x6, op_spec: 0x12, loopid:0x0, imm:0, Instr: 0x62400000
MS: opcode:0x6, op_spec: 0x1a, loopid:0x0, imm:0, Instr: 0x63400000
MS: opcode:0x7, op_spec: 0x0, loopid:0x0, imm:15, Instr: 0x7000000f
MS: opcode:0x6, op_spec: 0x2, loopid:0x0, imm:18, Instr: 0x60400012
MS: opcode:0x6, op_spec: 0xa, loopid:0x0, imm:16, Instr: 0x61400010
MS: opcode:0x6, op_spec: 0xb, loopid:0x0, imm:16, Instr: 0x61600010
MS: opcode:0x6, op_spec: 0x12, loopid:0x0, imm:0, Instr: 0x62400000
MS: opcode:0x6, op_spec: 0x1a, loopid:0x0, imm:0, Instr: 0x63400000
operation is <dnnweaver2.tensorOps.cnn.TypeCastOp object at 0x7ff94f2769e8>
OBUF.pop                  ->   R0
R0         >>  #(12)      ->   R0
R0                        -> ST-DDR.push
MS: opcode:0xa, op_spec: 0x0, loopid:0x0, imm:36, Instr: 0xa0000024
MS: opcode:0x9, op_spec: 0x0, loopid:0x0, imm:0, Instr: 0x90000000
MS: opcode:0x9, op_spec: 0x8, loopid:0x8, imm:7168, Instr: 0x91081c00
MS: opcode:0x9, op_spec: 0x9, loopid:0x0, imm:13, Instr: 0x9120000d
MS: opcode:0x7, op_spec: 0x0, loopid:0x0, imm:0, Instr: 0x70000000
MS: opcode:0x6, op_spec: 0x0, loopid:0x0, imm:1, Instr: 0x60000001
MS: opcode:0x7, op_spec: 0x0, loopid:0x0, imm:0, Instr: 0x70000000
MS: opcode:0x6, op_spec: 0x0, loopid:0x0, imm:16, Instr: 0x60000010
MS: opcode:0x7, op_spec: 0x0, loopid:0x0, imm:15, Instr: 0x7000000f
MS: opcode:0x6, op_spec: 0x0, loopid:0x0, imm:1, Instr: 0x60000001
MS: opcode:0x7, op_spec: 0x0, loopid:0x0, imm:15, Instr: 0x7000000f
MS: opcode:0x6, op_spec: 0x0, loopid:0x0, imm:16, Instr: 0x60000010
MS: opcode:0x7, op_spec: 0x0, loopid:0x0, imm:0, Instr: 0x70000000
MS: opcode:0x6, op_spec: 0x0, loopid:0x0, imm:1, Instr: 0x60000001
MS: opcode:0x7, op_spec: 0x0, loopid:0x0, imm:0, Instr: 0x70000000
MS: opcode:0x6, op_spec: 0x0, loopid:0x0, imm:256, Instr: 0x60000100
MS: opcode:0x7, op_spec: 0x5, loopid:0x5, imm:25, Instr: 0x70a50019
MS: opcode:0x5, op_spec: 0x2d, loopid:0x0, imm:0, Instr: 0x55a00000
MS: opcode:0x6, op_spec: 0x2d, loopid:0x0, imm:53248, Instr: 0x65a0d000
MS: opcode:0x6, op_spec: 0x36, loopid:0x0, imm:0, Instr: 0x66c00000
MS: opcode:0x6, op_spec: 0x3f, loopid:0x0, imm:0, Instr: 0x67e00000
MS: opcode:0x7, op_spec: 0x5, loopid:0x5, imm:25, Instr: 0x70a50019
MS: opcode:0x6, op_spec: 0x2d, loopid:0x0, imm:128, Instr: 0x65a00080
MS: opcode:0x6, op_spec: 0x36, loopid:0x0, imm:0, Instr: 0x66c00000
MS: opcode:0x6, op_spec: 0x3f, loopid:0x0, imm:0, Instr: 0x67e00000
MS: opcode:0x7, op_spec: 0x1, loopid:0x1, imm:15, Instr: 0x7021000f
MS: opcode:0x6, op_spec: 0x9, loopid:0x0, imm:1, Instr: 0x61200001
MS: opcode:0x7, op_spec: 0x1, loopid:0x1, imm:15, Instr: 0x7021000f
MS: opcode:0x6, op_spec: 0x9, loopid:0x0, imm:416, Instr: 0x612001a0
MS: opcode:0x7, op_spec: 0x1, loopid:0x1, imm:0, Instr: 0x70210000
MS: opcode:0x6, op_spec: 0x9, loopid:0x0, imm:1, Instr: 0x61200001
MS: opcode:0x7, op_spec: 0x1, loopid:0x1, imm:0, Instr: 0x70210000
MS: opcode:0x5, op_spec: 0x9, loopid:0x0, imm:2, Instr: 0x51200002
MS: opcode:0x6, op_spec: 0x9, loopid:0x0, imm:41984, Instr: 0x6120a400
MS: opcode:0x8, op_spec: 0x0, loopid:0x0, imm:255, Instr: 0x800000ff
MS: opcode:0x8, op_spec: 0x0, loopid:0x0, imm:1, Instr: 0x80000001
Number of instructions: 107
[   75497472 -1879048192 -1844080640 -1827287040 -1860823040 -1876951040
 -1843396606 -1826619390 -1860173822  1913651225  1611714816  1360003075
  1628454912  1362100227  1630552064  1645215744  1661992960  1913651225
  1611661440  1628439040  1630536192  1645215744  1661992960   270598145
  1881210897  1610678280  1881210897  1610681616   291635201   560070657
  1883373583  1627521056  1629618208  1883373583  1627534336  1629631488
   304283649  1885536258  1644363808  1885536258  1644363872   323223553
  1887698944  1661206528  1879048194  1614807041  1631584256  1633681408
  1648361473  1665138688  1879048194  1614807058  1631584256  1633681408
  1648361475  1665138688  1879048207  1614807041  1631584257  1633681409
  1648361472  1665138688  1879048207  1614807058  1631584272  1633681424
  1648361472  1665138688 -1610612700 -1879048192 -1861739520 -1860173811
  1879048192  1610612737  1879048192  1610612752  1879048207  1610612737
  1879048207  1610612752  1879048192  1610612737  1879048192  1610612992
  1889861657  1436549120  1705037824  1723858944  1742733312  1889861657
  1704984704  1723858944  1742733312  1881210895  1629487105  1881210895
  1629487520  1881210880  1629487105  1881210880  1361051650  1629529088
 -1342177152  -822080512 -1342177272 -2147483393 -2147483647]
