import pickle
import numpy as np
import sys
import copy

def transform(model_weight, num_columns):
    ret_weight = copy.deepcopy(model_weight)
    kernels = ret_weight["kernel"] 
    h, w, ic, oc = kernels.shape
    
    if oc % 4 != 0:
        new_oc = (int(oc / 4) + 1) * 4
        new_kernels = np.zeros([h, w, ic, new_oc]) 
        new_kernels[0:h, 0:w, 0:ic, 0:oc] = kernels
        kernels = new_kernels
        oc = new_oc
    
    split_kernels = np.reshape(kernels, (h, w, ic, int(oc / num_columns), num_columns))
    
    moving_kernels = np.swapaxes(split_kernels, 3, 2)
    moving_kernels = np.swapaxes(moving_kernels, 2, 1)
    updated_kernels = np.swapaxes(moving_kernels, 1, 0)

    ret_weight["kernel"] = updated_kernels

    return ret_weight 

def transform_dark2bitfusion(model_weight_list, num_columns):
    newlist = []
    for model_weight in model_weight_list:
        transformed_model_weight = transform(model_weight, num_columns)
        newlist.append(transformed_model_weight)
    return newlist

def run_modifydim(filename, num_columns):
    with open(filename, "rb") as handle:
        model_weight_list = pickle.load(handle)

    model_weight_list = transform_dark2bitfusion (model_weight_list, num_columns)

    return model_weight_list

def main():
    if len(sys.argv) != 3:
        print ("Usage: ./dark2bitfusion.py <pickle_filename> <num_columns>")
        sys.exit()
    else:
        filename = sys.argv[1]
        num_columns = int(sys.argv[2])

    model_weight_list = run_modifydim(filename, num_columns)

    with open("dim-" + filename, "wb") as handle:
        pickle.dump(model_weight_list, handle, protocol=2)

if __name__ == '__main__':
    main()
