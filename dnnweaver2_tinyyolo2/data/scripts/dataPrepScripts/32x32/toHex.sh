rm -rf image data1 data2 data3 data4 bias
mkdir image
mkdir data1
mkdir data2
mkdir data3
mkdir data4
mkdir bias

hexdump -v -e '/2 "%04x\n"' test_image.bin > image/image.txt

hexdump -v -e '/2 "%04x\n"' conv0_weight.bin   > data1/conv0_weight.txt
hexdump -v -e '/2 "%04x\n"' conv0_bias.bin     > bias/conv0_bias.txt
hexdump -v -e '/2 "%04x\n"' conv0_bn_mean.bin  > data1/conv0_bn_mean.txt
hexdump -v -e '/2 "%04x\n"' conv0_bn_scale.bin > data1/conv0_bn_scale.txt
hexdump -v -e '/2 "%04x\n"' conv1_weight.bin   > data1/conv1_weight.txt
hexdump -v -e '/2 "%04x\n"' conv1_bias.bin     > bias/conv1_bias.txt
hexdump -v -e '/2 "%04x\n"' conv1_bn_mean.bin  > data1/conv1_bn_mean.txt
hexdump -v -e '/2 "%04x\n"' conv1_bn_scale.bin > data1/conv1_bn_scale.txt
hexdump -v -e '/2 "%04x\n"' conv2_weight.bin   > data1/conv2_weight.txt
hexdump -v -e '/2 "%04x\n"' conv2_bias.bin     > bias/conv2_bias.txt
hexdump -v -e '/2 "%04x\n"' conv2_bn_mean.bin  > data1/conv2_bn_mean.txt
hexdump -v -e '/2 "%04x\n"' conv2_bn_scale.bin > data1/conv2_bn_scale.txt
hexdump -v -e '/2 "%04x\n"' conv3_weight.bin   > data1/conv3_weight.txt
hexdump -v -e '/2 "%04x\n"' conv3_bias.bin     > bias/conv3_bias.txt
hexdump -v -e '/2 "%04x\n"' conv3_bn_mean.bin  > data1/conv3_bn_mean.txt
hexdump -v -e '/2 "%04x\n"' conv3_bn_scale.bin > data1/conv3_bn_scale.txt
hexdump -v -e '/2 "%04x\n"' conv4_weight.bin   > data1/conv4_weight.txt
hexdump -v -e '/2 "%04x\n"' conv4_bias.bin     > bias/conv4_bias.txt
hexdump -v -e '/2 "%04x\n"' conv4_bn_mean.bin  > data1/conv4_bn_mean.txt
hexdump -v -e '/2 "%04x\n"' conv4_bn_scale.bin > data1/conv4_bn_scale.txt
hexdump -v -e '/2 "%04x\n"' conv5_weight.bin   > data1/conv5_weight.txt
hexdump -v -e '/2 "%04x\n"' conv5_bias.bin     > bias/conv5_bias.txt
hexdump -v -e '/2 "%04x\n"' conv5_bn_mean.bin  > data1/conv5_bn_mean.txt
hexdump -v -e '/2 "%04x\n"' conv5_bn_scale.bin > data1/conv5_bn_scale.txt

hexdump -v -e '/2 "%04x\n"' conv6_weight.bin   > data2/conv6_weight.txt
hexdump -v -e '/2 "%04x\n"' conv6_bias.bin     > bias/conv6_bias.txt
hexdump -v -e '/2 "%04x\n"' conv6_bn_mean.bin  > data2/conv6_bn_mean.txt
hexdump -v -e '/2 "%04x\n"' conv6_bn_scale.bin > data2/conv6_bn_scale.txt
hexdump -v -e '/2 "%04x\n"' conv7_weight.bin   > data3/conv7_weight.txt
hexdump -v -e '/2 "%04x\n"' conv7_bias.bin     > bias/conv7_bias.txt
hexdump -v -e '/2 "%04x\n"' conv7_bn_mean.bin  > data3/conv7_bn_mean.txt
hexdump -v -e '/2 "%04x\n"' conv7_bn_scale.bin > data3/conv7_bn_scale.txt
hexdump -v -e '/2 "%04x\n"' conv8_weight.bin   > data4/conv8_weight.txt
hexdump -v -e '/2 "%04x\n"' conv8_bias.bin     > bias/conv8_bias.txt
#hexdump -v -e '/2 "%04x\n"' conv8_bn_mean.bin  > data/conv8_bn_mean.txt
#hexdump -v -e '/2 "%04x\n"' conv8_bn_scale.bin > data/conv8_bn_scale.txt

tar -zcvf tiny_yolo2_image.tar.gz image/
tar -zcvf tiny_yolo2_data1.tar.gz data1/
tar -zcvf tiny_yolo2_data2.tar.gz data2/
tar -zcvf tiny_yolo2_data3.tar.gz data3/
tar -zcvf tiny_yolo2_data4.tar.gz data4/
tar -zcvf tiny_yolo2_bias.tar.gz bias/

