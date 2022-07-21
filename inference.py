import os
import glob
import json
import argparse

from pathlib import Path

# 0. to tfrecord
# 1. inference
# 2. convert task2GT of pred
# 3. convert OBB2HBB of GT
# 4. DOTA2COCO.py for both
# 5. use pycocotools from IQF

PROTOBUF_PY="/usr/local/bin/python"

def get_file_size(filename):
    return float(Path(filename).stat().st_size) / 1024 / 1024

def get_avg_file_size(glob_crit):
    size_sum = 0
    fnlst = glob.glob(glob_crit)
    for fn in fnlst:
        size = get_file_size(fn)
        size_sum+=size
    return size_sum/len(fnlst)

def main(
	trainds, outputpath,
	MODEL="rfcn_resnet101_coco_11_06_2017",
	CROPSZ=1024,
	CUDA_VISIBLE_DEVICES='2',
	STEPS = [0,1,2,3,4,5]
	):

	###############################
	# 0. to tfrecord
	###############################

	original_ds = (trainds.split('#')[0] if '#' in trainds else trainds)
	data_dir = trainds
	#data_dir = f'/Nas/DOTA1_0/split_ss_dota1_0_glasgow_{CROPSZ}/val'
	indexfile = os.path.join(trainds, f'val.txt')
	output_name = os.path.join(trainds, f'tf_records/dota_val.record')

	# make val.txt file
	txt='\n'.join(glob.glob(os.path.join(data_dir,f'images','*')))
	with open(f'{data_dir}/val.txt','w') as f:
		f.write(txt)

	cmd = [
		f"cd object_detection &&",
		f"{PROTOBUF_PY}",
		f"./create_dota_tf_record.py",
		f"--data_dir {data_dir}",
		f"--indexfile {indexfile}",
		f"--output_name {output_name}",
		f"--label_map_path data/dota_label_map.pbtxt",
	]
	
	if 0 in STEPS:
		print('**************************************\n\t\t\tSTEP 0\n**************************************')
		print(cmd)
		os.system( ' '.join(cmd) )

	###############################
	# 1. inference
	###############################

	cmd = [
		f"cd object_detection &&",
		f"{PROTOBUF_PY}",
		f"./getresultfromtfrecord.py",
		f"--model {MODEL}", # useless now
		f"--trainds {trainds}",
		f"--outputpath {outputpath}",
		f"--cu {CUDA_VISIBLE_DEVICES}",
	]

	if 1 in STEPS:
		print('**************************************\n\t\t\tSTEP 1\n**************************************')
		print(cmd)
		os.system( ' '.join(cmd) )

	###############################
	# 2. convert task2HBB of pred
	###############################

	cmd = [
		"cd DOTA_devkit &&",
		f"{PROTOBUF_PY}",
		"./task2gt.py",
		f"--outputpath {outputpath}"
	]

	if 2 in STEPS:
		print('**************************************\n\t\t\tSTEP 2\n**************************************')
		print(cmd)
		os.system( ' '.join(cmd) )

	# ###############################
	# # 3. convert OBB2HBB of GT
	# ###############################

	OBBDIR = os.path.join(original_ds,'labelTxt')
	HBBDIR = os.path.join(original_ds,'labelTxtHBB')

	cmd = [
		"cd DOTA_devkit &&",
		f"{PROTOBUF_PY}",
		"./results_obb2hbb.py",
		f"--obbdir {OBBDIR}",
		f"--hbbdir {HBBDIR}"
	]

	if 3 in STEPS:
		print('**************************************\n\t\t\tSTEP 3\n**************************************')
		print(cmd)
		os.system( ' '.join(cmd) )

	# ###############################
	# # 4. DOTA2COCO.py for both
	# ###############################

	cmd = [
		"cd DOTA_devkit",
		"&&",
		f"{PROTOBUF_PY}",
		"./DOTA2COCO.py",
		f"--is_gt true",
		f"--img_id_reference_coco_fn {original_ds}", # reference file
		f"--outputpath {original_ds}" # out
		"&&",
		f"{PROTOBUF_PY}",
		"./DOTA2COCO.py",
		f"--is_gt false",
		f"--img_id_reference_coco_fn {original_ds}", # reference file
		f"--outputpath {outputpath}" # out
	]

	if 4 in STEPS:
		print('**************************************\n\t\t\tSTEP 4\n**************************************')
		print(cmd)
		os.system( ' '.join(cmd) )

	# ###############################
	# # 5. use pycocotools from IQF
	# ###############################

	if 5 in STEPS:

		print('**************************************\n\t\t\tSTEP 5\n**************************************')
		print(cmd)

		from iquaflow.metrics import BBDetectionMetrics

		bbmet = BBDetectionMetrics()
		results = bbmet.apply(
			predictions=os.path.join(outputpath,'output.json'),
			gt_path=os.path.join(trainds,'coco.json')
		)

		# metric format (list)
		results = { k:[results[k]] for k in results }
		# more metrics
		results['format'] = (
			glob.glob(os.path.join(outputpath,'images','*'))[0].split('.')[-1]
			if not os.path.isdir(os.path.join(outputpath,'images_compressed'))
			else glob.glob(os.path.join(outputpath,'images_compressed','*'))[0].split('.')[-1]
			)
			
		results['Mb'] = [ (
			get_avg_file_size(os.path.join(outputpath,'images','*'))
			if not os.path.isdir(os.path.join(outputpath,'images_compressed'))
			else get_avg_file_size(os.path.join(outputpath,'images_compressed','*'))
			) ]
		# add hyperparams
		results['MODEL'] = MODEL
		results['CROPSZ'] = CROPSZ

		# results['quality'] = 101
		# results['scaleperc'] = 101
		# results['bits'] = 9

		with open(os.path.join(outputpath,'results.json'), 'w') as outfile:
			json.dump(results, outfile)

if __name__=='__main__':

	parser = argparse.ArgumentParser()
	parser.add_argument('--trainds', type=str, default='/data/DOTA1_0/split_ss_dota1_0_glasgow_1024/val', help='input dataset path')
	parser.add_argument('--outputpath', type=str, default='/iqf/outputpath', help='input dataset path')
	#parser.add_argument('--cropsz', type=int, default=1024, help='crop size')
	parser.add_argument('--steps', type=str, default='0,1,2,3,4,5', help='CUDA_VISIBLE_DEVICES')
	parser.add_argument('--cu', type=str, default='0,1', help='CUDA_VISIBLE_DEVICES')
	parser.add_argument('--model',
		type=str,
		default='/data/DOTA1_0/split_ss_dota1_0_glasgow_1024/train/chkpt/dota_rfcn_output_2000000_136610/frozen_inference_graph.pb',
		help='model full subfolder name'
	)
	opt = parser.parse_args()

	# import sys; print(f'{sys.argv}'); raise 'sdfsdf'

	CUDA_VISIBLE_DEVICES = opt.cu
	os.environ['CUDA_VISIBLE_DEVICES'] = opt.cu

	trainds    = opt.trainds
	outputpath = opt.outputpath

	STEPS  = [int(s) for s in opt.steps.split(',')]
	MODEL  = opt.model
	CROPSZ = os.path.basename(os.path.dirname(trainds)).split('_')[-1]

	if '#' in opt.trainds:
		# copy labelTxt from original
		original_ds = os.path.join( opt.trainds.split('#')[0], 'labelTxt' )
		os.system(f'ln -sf {original_ds} {opt.trainds}')

	main(
		trainds,
		outputpath,
		MODEL,
		CROPSZ,
		CUDA_VISIBLE_DEVICES,
		STEPS
		)