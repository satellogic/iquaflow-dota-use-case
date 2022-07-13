import os
import shutil
import argparse
import dota_utils as util

if __name__=='__main__':

    parser = argparse.ArgumentParser()
    
    # parser.add_argument('--model', type=str, default='rfcn_resnet101_coco_11_06_2017', help='initial weights subpath')
    # parser.add_argument('--cropsz', type=int, default=1024, help='crop size')
    parser.add_argument('--outputpath', type=str, default='/iqf/outputpath', help='outputpath')
    
    opt = parser.parse_args()
    
    # cropsz = opt.cropsz
    # model = opt.model

    # src = f'/Nas/DOTA1_0/split_ss_dota1_0_glasgow_{cropsz}/results/{model}/split'
    # dst =  f'/Nas/DOTA1_0/split_ss_dota1_0_glasgow_{cropsz}/results/{model}/labelTxt'
    src = os.path.join(opt.outputpath, f'split')
    dst = os.path.join(opt.outputpath, 'labelTxt')

    shutil.rmtree(dst,ignore_errors=True)
    os.makedirs(dst,exist_ok=True)
    util.Task2groundtruth_poly(src, dst )
