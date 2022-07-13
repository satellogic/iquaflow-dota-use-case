FROM floydhub/tensorflow:1.5.0-gpu.cuda8cudnn6-py3_aws.22

ENV DEBIAN_FRONTEND=noninteractive
ENV LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH
ENV PATH=/usr/local/cuda/bin:$PATH
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV CONDA_DIR $HOME/miniconda3
ENV PATH=$CONDA_DIR/bin:$PATH
ENV APP_PATH=/iqf

RUN sed -i 's;http://archive.debian.org/debian/;http://deb.debian.org/debian/;' /etc/apt/sources.list
RUN apt-get -y --allow-unauthenticated update
RUN apt-get -o Dpkg::Options::="--force-confold" upgrade -q -y --force-yes
#apt-get -y --allow-unauthenticated --allow -q upgrade
RUN apt-get -y --allow-unauthenticated update

RUN apt -y install wget && \
	apt -y install git && \
	apt -y install libglib2.0-0 && \
	apt -y install libgl1-mesa-glx

WORKDIR $APP_PATH
ENV PYTHONPATH=$PYTHONPATH:$APP_PATH:$APP_PATH/slim

# Install Protobuf 2.6
RUN	wget https://github.com/google/protobuf/releases/download/v2.6.1/protobuf-2.6.1.tar.gz && \
	chmod 775 protobuf-2.6.1.tar.gz && \
	tar xzf protobuf-2.6.1.tar.gz && \
	cd protobuf-2.6.1 && \
	apt-get -y update && \
	apt-get -y install build-essential && \
	./configure && \
	make && \
	make check && \
	make install && \
	ldconfig && \
	cd $APP_PATH

RUN pip install --upgrade pip && \
	#pip install nbconvert==5.3.1 && \
	#pip install tornado==4.2 && \
	pip install jupyterlab==2.3.2 && \
	pip install shapely

# #############################
ENV CONDA_DIR $HOME/miniconda3
ENV PATH=$CONDA_DIR/bin:$PATH
RUN echo ". $CONDA_DIR/etc/profile.d/conda.sh" >> ~/.profile
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
	chmod 775 Miniconda3-latest-Linux-x86_64.sh && \
	bash Miniconda3-latest-Linux-x86_64.sh -b -p $CONDA_DIR && \
	rm Miniconda3-latest-Linux-x86_64.sh && \
	$CONDA_DIR/bin/conda create -n iqfenv python=3.6 -q -y && \
	$CONDA_DIR/bin/conda run -n iqfenv pip install git+https://gitlab+deploy-token-45:FKSA3HpmgUoxa5RZ69Cf@publicgitlab.satellogic.com/iqf/iquaflow-

RUN rm /usr/local/share/jupyter/kernels/python3/kernel.json
COPY ./kernel.json /usr/local/share/jupyter/kernels/python3/kernel.json

CMD ["/bin/bash", "-c", "./startup.sh && /bin/bash"]