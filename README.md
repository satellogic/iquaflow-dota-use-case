# iq-dota-use-case

This is a study of object detector performance degradation with different level of compression added to the input images.
The core inference model code is from __dota_models__, see the main section below.
____________________________________________________________________________________________________


## To reproduce the experiments:

1. `git clone git@publicgitlab.satellogic.com:iqf/iq-dota-use-case`
2. `cd iq-dota-use-case`
3. Then build the docker image with `make build`. This will also download the dataset and weights.
4. In order to execute the experiments:
    - `make dockershell` (\*)
    - Inside the docker terminal execute `python ./iqf-usecase.py`
5. Start the mlflow server by doing `make mlflow` (\*)
6. Notebook examples can be launched and executed by `make notebookshell NB_PORT=[your_port]"` (\**)
7. To access the notebook from your browser in your local machine you can do:
    - If the executions are launched in a server, make a tunnel from your local machine. `ssh -N -f -L localhost:[your_port]:localhost:[your_port] [remote_user]@[remote_ip]`  Otherwise skip this step.
    - Then, in your browser, access: `localhost:[your_port]/?token=IQF`


____________________________________________________________________________________________________

## Notes

   - The results of the IQF experiment can be seen in the MLflow user interface.
   - For more information please check the IQF_expriment.ipynb or IQF_experiment.py.
   - There are also examples of dataset Sanity check and Stats in SateAirportsStats.ipynb
   - The default ports are `8811` for the notebookshell, `5000` for the mlflow
   - (*)
        Additional optional arguments can be added. The dataset location is:
        >`DS_VOLUME=[path_to_your_dataset]`
   - To change the default port for the mlflow service:
     >`MLF_PORT=[your_port]`
   - (**)
        To change the default port for the notebook: 
        >`NB_PORT=[your_port]`
   - A terminal can also be launched by `make dockershell` with optional arguments such as (*)
   - (***)
        Depending on the version of your cuda drivers and your hardware you might need to change the version of pytorch which is specified as an install instruction in the Dockerfile.

# DOTA_models

We provide the config files, TFRecord files and label_map file used in training [DOTA](http://captain.whu.edu.cn/DOTAweb/dataset.html) with ssd and rfcn, and the trained models have been uploaded to Baidu Drive.   
Notice that our code is tested on official [Tensorflow models@(commit fe2f8b01c6)](https://github.com/tensorflow/models/tree/fe2f8b01c686fd62272c3992686a637db926ce5c) with [tf-nightly-gpu (1.5.0.dev20171102)](https://pypi.org/project/tf-nightly-gpu/), cuda-8.0 and cudnn-6.0 on Ubuntu 16.04.1 LTS.

## Installation
- [Tensorflow](https://pypi.org/project/tf-nightly-gpu/):
  ```bash
      pip install tf-nightly-gpu==1.5.0.dev20171102
  ```
- [Object Detection API](https://github.com/ringringyi/DOTA_models/tree/master/object_detection)<br>
  Follow the instructions in [Installation](https://github.com/ringringyi/DOTA_models/blob/master/object_detection/g3doc/installation.md). Note the version of Protobuf.
- [Development kit](https://github.com/CAPTAIN-WHU/DOTA_devkit)<br>
  You can easily install it following the instructions in [readme](https://github.com/CAPTAIN-WHU/DOTA_devkit/blob/master/readme.md).

## Preparing inputs
Tensorflow Object Detection API reads data using the TFRecord file format. The raw DOTA data set is located [here](http://captain.whu.edu.cn/DOTAweb/dataset.html). To download, extract and convert it to TFRecords, run the following commands
below:
```bash
# From tensorflow/models/object_detection/
python create_dota_tf_record.py \
    --data_dir=/your/path/to/dota/train \
    --indexfile=train.txt \
    --output_name=dota_train.record \
    --label_map_path=data/dota_label_map.pbtxt \
```
The subdirectory of "data_dir" is in the structure of
```
data_dir
    ├── images
    └── labelTxt
    └── indexfile
```
Here the indexfile contains the full path of all images to convert, such as `train.txt` or `test.txt`. Its format is shown below.
```
/your/path/to/dota/train/images/P2033__1__0___0.png
/your/path/to/dota/train/images/P2033__1__0___595.png
...
```
And the output path of tf_record is also under "data_dir", you can easily find it in `data_dir/tf_records/`

## Training
A local training job can be run with the following command:

```bash
# From tensorflow/models/object_detection/
python train.py \
    --logtostderr \
    --pipeline_config_path=${PATH_TO_YOUR_PIPELINE_CONFIG} \
    --train_dir=${PATH_TO_TRAIN_DIR}
```
The pipline config file for DOTA data set can be found at `models/model/rfcn_resnet101_dota.config` or  `models/model/ssd608_inception_v2_dota608.config`. You need to replace some paths in it with your own paths.

Here we train rfcn with image size of 1024×1024, ssd with image size of 608×608. Please refer to [DOTA_devkit/ImgSplit.py](https://github.com/CAPTAIN-WHU/DOTA_devkit/blob/master/ImgSplit.py) to split the picture and label. The trained models can be downloaded here:<br>
* Baidu Drive: [rfcn](https://pan.baidu.com/s/15fFYrffdF94UzA5tYq6ToQ), [ssd](https://pan.baidu.com/s/1Gg4KYlqBtyp83DHJW1qTxg)<br>
* Google Drive: [rfcn](https://drive.google.com/open?id=1IIyTRcV1LcCqiyU1xTWftOnOD015ka2P), [ssd](https://drive.google.com/open?id=1Kt82V0PG4hJ6rCsFDnrhAGTbOw0v7xYK)

## Evaluation
You can use the pre-trained models to test images. Modify paths in `getresultfromtfrecord.py` and then run with the following commad:
```bash
# From tensorflow/models/object_detection/
python getresultfromtfrecord.py
```
Then you will obtain 15 files in the specified folder. For DOTA, you can submit your results on [Task2 - Horizontal Evaluation Server](http://captain.whu.edu.cn/DOTAweb/evaluation.html) for evaluation. Make sure your submission is in the correct format. 
