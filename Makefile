
PROJ_NAME=dota
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
	@echo "notebookshell -- launches a notebook server"
	@echo "mlflow -- launches an mlflow server"

build:
	docker build -t $(IMG) .
	chmod 775 ./download.sh && ./download.sh

dockershell:
	docker run --rm --name $(CONTAINER_NAME) --gpus all -p 9198:9198 \
	-v $(shell pwd):$(APP_PATH) -v $(DS_VOLUME):$(DS_VOLUME) \
	-it $(IMG)

notebookshell:
	docker run --gpus all --privileged -itd --rm --name $(CONTAINER_NAME)-nb \
	-p ${NB_PORT}:${NB_PORT} \
	-v $(shell pwd):$(APP_PATH) -v $(DS_VOLUME):$(DS_VOLUME) \
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
	-v $(shell pwd):$(APP_PATH) -v $(DS_VOLUME):$(DS_VOLUME) \
	$(IMG) \
	mlflow ui --host 0.0.0.0:${MLF_PORT}