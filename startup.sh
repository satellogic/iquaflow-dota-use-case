export PROTO_PY=/usr/local/bin/python
protoc object_detection/protos/*.proto --python_out=.
$PROTO_PY object_detection/builders/model_builder_test.py

# #############################
# export CONDA_DIR=$HOME/miniconda3
# export CONDA_AUTO_ACTIVATE_BASE=false
# #ENV PATH=$CONDA_DIR/bin:$PATH
# echo ". $CONDA_DIR/etc/profile.d/conda.sh" >> ~/.profile
# # RUN apt install wget 
# # RUN apt -y install git
# # RUN apt install libglib2.0-0 -y 
# # RUN apt install libgl1-mesa-glx -y 
# #RUN export PATH="$HOME/miniconda3/bin:$PATH" 
# export CONDA_DIR=$HOME/miniconda3
# export CONDA_AUTO_ACTIVATE_BASE=false
# wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
# chmod 775 Miniconda3-latest-Linux-x86_64.sh && \
# bash Miniconda3-latest-Linux-x86_64.sh -b -p $CONDA_DIR && \
# rm Miniconda3-latest-Linux-x86_64.sh && \
# $CONDA_DIR/bin/conda create -n iqfenv python=3.6 -q -y && \
# $CONDA_DIR/bin/conda run -n iqfenv pip install -qq git+https://gitlab+deploy-token-45:FKSA3HpmgUoxa5RZ69Cf@publicgitlab.satellogic.com/iqf/iquaflow-
# $CONDA_DIR/bin/conda run -n iqfenv pip install -qq jupyterlab
# echo "iqf env is: $CONDA_DIR/envs/iqfenv "
# #############################