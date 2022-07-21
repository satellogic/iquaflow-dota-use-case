
PROJ_NAME=dotahbb
APP_PATH=/iqf

IMG="${PROJ_NAME}"
CONTAINER_NAME="${PROJ_NAME}-${USER}"

ifndef DS_VOLUME
	DS_VOLUME=/Nas
endif

ifndef NB_PORT
	NB_PORT=8811
endif

ifndef MLF_PORT
	MLF_PORT=5000
endif

help:
	@echo "build -- builds the docker image"
	@echo "dockershell -- raises an interactive shell docker"
	@echo "preproc -- this preprocesses the dataset and downloads trained models"
	@echo "notebookshell -- launches a notebook server"
	@echo "mlflow -- launches an mlflow server"

build:
	docker build -t $(IMG) .

dockershell:
	docker run --rm --name $(CONTAINER_NAME) --gpus all -p 9198:9198 \
	-v $(shell pwd):$(APP_PATH) -v $(DS_VOLUME):/data \
	-it $(IMG)

download:
	docker exec -it $(CONTAINER_NAME) /bin/bash -c "./download.sh"

notebookshell:
	docker run --gpus all --privileged -itd --rm --name $(CONTAINER_NAME)-nb \
	-p ${NB_PORT}:${NB_PORT} \
	-v $(shell pwd):$(APP_PATH) -v $(DS_VOLUME):/data \
	$(IMG) \
	/miniconda3/envs/iqfenv/bin/jupyter lab \
	--NotebookApp.token='iqf' \
	--no-browser \
	--ip=0.0.0.0 \
	--allow-root \
	--port=${NB_PORT}

mlflow:
	docker run --privileged -itd --rm --name $(CONTAINER_NAME)-mlf \
	-p ${MLF_PORT}:${MLF_PORT} \
	-v $(shell pwd):$(APP_PATH) -v $(DS_VOLUME):/data \
	$(IMG) \
	mlflow ui --host 0.0.0.0:${MLF_PORT}