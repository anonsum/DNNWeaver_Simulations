import os
import pickle
import numpy as np
import sys
import copy
import math
import json
import collections

import fraqnn.benchmarks

op_list = []
op_list_len = 0
op_list_index = 0
params = collections.OrderedDict()

def fp32tofxp16_tensor(tensor, num_frac_bits):
    pow_nfb_tensor = np.full(tensor.shape, pow(2, num_frac_bits), dtype=np.int32)
    shifted_tensor = tensor * pow_nfb_tensor
    casted_tensor = np.int16(shifted_tensor)
    return casted_tensor

def fxp16tofp32_tensor(tensor, num_frac_bits):
    pow_nfb_tensor = np.full(tensor.shape, np.float32(pow(2, num_frac_bits)), dtype=np.float32)
    shifted_tensor = np.float32(tensor) / pow_nfb_tensor
    return shifted_tensor

def fxp64tofxp16_3d(tensor_3d, num_frac_bits):
    new_tensor = np.zeros(tensor_3d.shape, dtype=np.int16)
    pow_nfb = pow(2, num_frac_bits)
    for i in range(0, len(tensor_3d)):
        itensor = tensor_3d[i]
        for j in range(0, len(itensor)):
            ijtensor = itensor[j]
            for k in range(0, len(ijtensor)):
                new_tensor[i][j][k] = np.int16(ijtensor[k] >> num_frac_bits)
    return new_tensor

def get_scale(variance, gamma):
    inv = 1.0 / np.sqrt(variance + np.full(variance.shape, 1e-5))
    scale = inv * gamma
    return scale

def fp32tofxp16_model_weights(model_weight, model_index, frac_bits, index_map, bswap):
    global op_list_index
    global params

    _model_weight = collections.OrderedDict()
    _model_weight["kernel"] = model_weight["kernel"]
    _model_weight["biases"] = model_weight["biases"]
    for key in model_weight.keys():
        if key == "kernel" or key == "biases":
            continue
        _model_weight[key] = model_weight[key]

    if (not "scale" in model_weight.keys()) and ("moving_variance" in model_weight.keys()):
        _model_weight["scale"] = get_scale(model_weight["moving_variance"], model_weight["gamma"])
    ret_weight = copy.deepcopy(_model_weight)

    for key in _model_weight.keys():
        if key == "kernel":
            kernels = ret_weight[key]
            print ("Shape: " + str(kernels.shape))
            oc, h, w, ic = kernels.shape

            new_kernels = np.zeros([oc, h, w, ic], dtype=np.int16)

            total_num = oc * h * w * ic 

            cnt = 0
            if not bswap:
                pow_nfb = pow(2, frac_bits[index_map["conv" + str(model_index)]]["w"])
            else:
                pow_nfb = pow(2, frac_bits[index_map["conv_bias" + str(model_index)]]["w"])
            for ocin in range(0, oc):
                ocarr = kernels[ocin]
                for hin in range(0, h):
                    harr = ocarr[hin]
                    for win in range(0, w):
                        warr = harr[win]
                        for icin in range(0, ic):
                            new_kernels[ocin][hin][win][icin] = np.int16(warr[icin] * pow_nfb)
                            # TODO: See if this change is correct
#                            new_kernels[ocin][hin][win][icin] = fp32tofxp16_val(warr[icin], pow_nfb)
                            cnt += 1
                            if cnt % (int(total_num / 5)) == 0:
                                sys.stdout.write(str(int(math.ceil(float(cnt) / float(total_num) * 10)) * 10) + "% done.. ")
                                sys.stdout.flush()
            print (" ")

            ret_weight["kernel"] = copy.deepcopy(new_kernels)

            # FraqNN Graph Building
            if not op_list[op_list_index] in params.keys():
                params[op_list[op_list_index]] = collections.OrderedDict()
            new_kernels = np.transpose(new_kernels, (3,0,1,2))
            params[op_list[op_list_index]]["weights"] = new_kernels
        elif key == "biases":
            if not bswap:
                pow_nfb = pow(2, frac_bits[index_map["bias" + str(model_index)]]["o"])
            else:
                pow_nfb = pow(2, frac_bits[index_map["conv_bias" + str(model_index)]]["b"])
            tensor = ret_weight[key]
            length = tensor.shape[0]
            # To match with Hardik's hardware, we adjust the bias value so that it becomes bias / scale
            if not bswap:
                new_tensor = np.zeros([length], dtype=np.int16)
                for i in range(0, length):
                    new_tensor[i] = np.int16(tensor[i] * pow_nfb)
                    # TODO: See if this change is correct
#                    new_tensor[i] = fp32tofxp16_val(tensor[i], pow_nfb)
            else:
                new_tensor = np.zeros([length], dtype=np.int32)
                for i in range(0, length):
                    # TODO: See if this change is correct
                    new_tensor[i] = np.int32(tensor[i] * pow_nfb)
#                    new_tensor[i] = fp32tofxp32_val(tensor[i], pow_nfb)

            ret_weight["biases"] = new_tensor

            # FraqNN Graph Buidling
            params[op_list[op_list_index]]["bias"] = new_tensor
            if op_list_index + 1 < len(op_list):
                op_list_index += 1
        else:
            if key == "scale":
                pow_nfb = pow(2, frac_bits[index_map["bn" + str(model_index)]]["s"])
            else:
                if not bswap:
                    pow_nfb = pow(2, frac_bits[index_map["conv" + str(model_index)]]["o"]) # because of (x - mean), mean's nfb should be matched with the prev conv's output
                else:
                    pow_nfb = pow(2, frac_bits[index_map["conv_bias" + str(model_index)]]["o"]) # because of (x - mean), mean's nfb should be matched with the prev conv's output

            tensor = ret_weight[key]
            length = tensor.shape[0]
            new_tensor = np.zeros([length], dtype=np.int16)
            for i in range(0, length):
                # TODO: See if this change is correct
                new_tensor[i] = np.int16(tensor[i] * pow_nfb)
#                new_tensor[i] = fp32tofxp16_val(tensor[i], pow_nfb)

            ret_weight[key] = new_tensor

            # FraqNN Graph Building
            if not op_list[op_list_index] in params.keys():
                params[op_list[op_list_index]] = collections.OrderedDict()
            if key == "moving_mean":
                params[op_list[op_list_index]]["mean"] = new_tensor
            elif key == "scale":
                params[op_list[op_list_index]]["scale"] = new_tensor
                op_list_index += 1
            
    return ret_weight

def fp32tofxp16_model_weight_list(model_weight_list, frac_bits, index_map, bswap):
    newlist = []
    for model_index in range(len(model_weight_list)):
        model_weight = model_weight_list[model_index]
        converted_model_weight = fp32tofxp16_model_weights(model_weight, model_index, frac_bits, index_map, bswap)
        newlist.append(converted_model_weight)
    return newlist

def run_fp32tofxp16_picklefile(filepath, frac_bits, index_map, bswap):
    with open(filepath, "rb") as handle:
        model_weight_list = pickle.load(handle)

    model_weight_list = fp32tofxp16_model_weight_list(model_weight_list, frac_bits, index_map, bswap)

    return model_weight_list

def gen_fraqnn_op_list():
    global op_list

    yolo_graph = fraqnn.benchmarks.get_graph('yolo2-tiny', train=False)
    for opname, _ in yolo_graph.op_registry.iteritems():
        if "TypeCastOp" in opname or "MaxPooling" in opname or "leakyReLU" in opname:
            continue
        op_list.append(opname)


def save_fraqnn_graph(filepath, input_name):
    dirname = os.path.dirname(filepath)
    filename = os.path.basename(filepath)
    fraqnn_filepath = dirname + "/fraqnn-" + str(input_name) + "-" + str(filename)

    with open(fraqnn_filepath, "wb") as h:
        pickle.dump(params, h, protocol=2)

def print_usage():
    print ("Usage: ./fp32tofxp16.py <org|bswap> <input_name> <pickle_filepath> <frac_bits_json> <index_map_json>")
    sys.exit()

def main():
    if len(sys.argv) != 6:
        print_usage()
    else:
        if not (sys.argv[1] == "org" or sys.argv[1] == "bswap"):
            print_usage()
        else:
            if sys.argv[1] == "org":
                bswap = False
            elif sys.argv[1] == "bswap":
                bswap = True
        input_name = sys.argv[2]
        filepath = sys.argv[3]
        frac_bits_json = sys.argv[4]
        index_map_json = sys.argv[5]

    with open(frac_bits_json) as f:
        frac_bits = json.load(f)
    with open(index_map_json) as f:
        index_map = json.load(f)

    gen_fraqnn_op_list()
    model_weight_list = run_fp32tofxp16_picklefile(filepath, frac_bits, index_map, bswap)
    save_fraqnn_graph(filepath, input_name)

    dirname = os.path.dirname(filepath)
    filename = os.path.basename(filepath)
    fxp16_filename = dirname + "/fxp16-" + str(input_name) + "-" + filename

    with open(fxp16_filename, "wb") as handle:
        pickle.dump(model_weight_list, handle, protocol=2) 
    
if __name__ == '__main__':
    main()
