import sys
import os
import pickle
import copy
import numpy as np
import collections



def print_usage():
    print ("Usage: ./weight_bswap.py <weight_pickle_filename>")

def bias_swap(pickle_filename):
    with open(pickle_filename, "rb") as h:
        model_weight_list = pickle.load(h)

    new_model_weight_list = [] 

    for i in range(len(model_weight_list)):
        new_model_weight = collections.OrderedDict()
        model_weight = model_weight_list[i]

        new_model_weight["kernel"] = model_weight["kernel"]
        if "moving_variance" in model_weight.keys():
            b = model_weight["biases"]
            v = model_weight["moving_variance"]
            g = model_weight["gamma"]
            s = (1.0 / np.sqrt(v + 1e-5)) * g
            new_model_weight["biases"] = b / s
            new_model_weight["moving_variance"] = v
            new_model_weight["gamma"] = g
            new_model_weight["moving_mean"] = model_weight["moving_mean"]
            new_model_weight["scale"] = s
        else:
            new_model_weight["biases"] = model_weight["biases"]
        new_model_weight_list.append(new_model_weight)

    pickle_dir = os.path.dirname(pickle_filename)
    pickle_filename = os.path.basename(pickle_filename)
    bswap_filename = pickle_dir + "/bswap-" + pickle_filename

    with open(bswap_filename, "wb") as h:
        pickle.dump(new_model_weight_list, h, protocol=2)

def main():
    if len(sys.argv) != 2:
        print_usage()
        sys.exit()

    pickle_filename = sys.argv[1]
    bias_swap(pickle_filename)

if __name__ == '__main__':
    main()
