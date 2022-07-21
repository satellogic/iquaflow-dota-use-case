#!/bin/bash

export DS_VOLUME=/data

for CROPSIZE in 608 1024
do
    export CROPSIZE=$CROPSIZE
    python3 -c "import os; D=os.environ['DS_VOLUME']; C=os.environ['CROPSIZE']; os.makedirs(f'{D}/DOTA1_0/split_ss_dota1_0_glasgow_{C}',exist_ok=True)"
    cd $DS_VOLUME/DOTA1_0/split_ss_dota1_0_glasgow_$CROPSIZE
    for PARTITION in "train" "val"
    do

python3 -c "
import os
import glob
for partition in os.listdir():
    txt='\n'.join(glob.glob(os.path.join(os.getcwd(),f'{partition}/images','*')))
    with open(f'{partition}/{partition}.txt','w') as f:
        f.write(txt)
"

    done
done

# Operations within object_detection module:

cd /iqf/object_detection

for CROPSIZE in 608 1024
do
    for PARTITION in "train" "val"
    do
        /usr/local/bin/python3 create_dota_tf_record.py \
            --data_dir=/data/DOTA1_0/split_ss_dota1_0_glasgow_$CROPSIZE/$PARTITION \
            --indexfile=$PARTITION.txt \
            --output_name=dota_$PARTITION.record \
            --label_map_path=data/dota_label_map.pbtxt
    done
done

# download pretrained RFCN model. http://download.tensorflow.org/models/object_detection/rfcn_resnet101_coco_11_06_2017.tar.gz
wget -O ./f.tar.gz https://image-quality-framework.s3.eu-west-1.amazonaws.com/iq-dota-use-case/models/dota_rfcn_output_2000000_136610.tar.gz && \
chmod 775 ./f.tar.gz && \
tar -zvxf ./f.tar.gz --no-same-owner && \
rm ./f.tar.gz

# download pretrained SSD model. http://download.tensorflow.org/models/object_detection/ssd_inception_v2_coco_11_06_2017.tar.gz
wget -O ./f.tar.gz https://image-quality-framework.s3.eu-west-1.amazonaws.com/iq-dota-use-case/models/dota608_ssd608_output_1243788.tar.gz && \
chmod 775 ./f.tar.gz && \
tar -zvxf ./f.tar.gz --no-same-owner && \
rm ./f.tar.gz