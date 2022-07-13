git add add_git.sh startup.sh download.sh
git add .gitignore Dockerfile Makefile LICENSE README.md requirements.txt kernel.json
git add IQF-UseCase.ipynb 
git add custom_iqf.py inference.py iqf-usecase.py 

cd DOTA_devkit
rm -rf ./.ipynb_checkpoints
rm -rf ./__pycache__
git add readme.md *.cpp *.h *.i
git add *.py
cd poly_nms_gpu
rm -rf ./.ipynb_checkpoints
rm -rf ./__pycache__
git add *.py *.hpp *.pyx *.cu Makefile
cd ..
cd ..
