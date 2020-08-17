#!/local/workspace/tools/anaconda2/bin/python2.7
import os
##  set path to caffe tool chain 
build_path = '/local/workspace/ee207432/caffe/build/tools'
command = build_path + '/caffe train --solver=../prototxt/lenet/lenet_solver.prototxt $@'
os.system(command)
