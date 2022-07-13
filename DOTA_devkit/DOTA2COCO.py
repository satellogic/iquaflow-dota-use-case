import dota_utils as util
import os
import cv2
import json
import argparse

wordname_15 = ['plane', 'baseball-diamond', 'bridge', 'ground-track-field', 'small-vehicle', 'large-vehicle', 'ship', 'tennis-court',
               'basketball-court', 'storage-tank',  'soccer-ball-field', 'roundabout', 'harbor', 'swimming-pool', 'helicopter']

def DOTA2COCO(srcpath, destfile, is_gt=True, fn_img_id_ref_gt=None):
    
    prefix = ('labelTxtHBB' if is_gt else 'labelTxt')
    detection_format = not is_gt
    if fn_img_id_ref_gt and not is_gt:
        with open(fn_img_id_ref_gt,'r') as jsonf:
            gtref = json.load(jsonf)
    
    imageparent = os.path.join(srcpath, 'images')
    labelparent = os.path.join(srcpath, prefix)
    
    data_dict = {}
    info = {'contributor': 'captain group',
           'data_created': '2018',
           'description': 'This is 1.0 version of DOTA dataset.',
           'url': 'http://captain.whu.edu.cn/DOTAweb/',
           'version': '1.0',
           'year': 2018}
    data_dict['info'] = info
    data_dict['images'] = []
    data_dict['categories'] = []
    data_dict['annotations'] = []
    
    for idex, name in enumerate(wordname_15):
        single_cat = {'id': idex + 1, 'name': name, 'supercategory': name}
        data_dict['categories'].append(single_cat)
    
    inst_count = 1
    image_id = 1
    with open(destfile, 'w') as f_out:
        filenames = util.GetFileFromThisRootDir(labelparent)
        for file in filenames:
            basename = util.custombasename(file)
            # image_id = int(basename[1:])

            imagepath = os.path.join(imageparent, basename + '.png')
            img = cv2.imread(imagepath)
            height, width, c = img.shape

            single_image = {}
            single_image['file_name'] = basename + '.png'
            single_image['id'] = image_id
            single_image['width'] = width
            single_image['height'] = height
            data_dict['images'].append(single_image)

            # annotations
            with open(file,'r') as fobj:

                line_lst = fobj.readlines()

                lst_lst = [
                    line.split(' ')
                    for line in line_lst
                ]

            objects = []
            for lst in lst_lst:
                obj = {}
                xmin = float(lst[0])
                ymin = float(lst[1])
                xmax = float(lst[2])
                ymax = float(lst[3])
                width, height = xmax - xmin, ymax - ymin
                obj['bbox']= xmin, ymin, width, height
                obj['name']= lst[-1].replace('\n','')
                obj['area']= width*height
                objects.append(obj)

            #objects = util.parse_dota_rec(file)

            for obj in objects:
                single_obj = {}
                single_obj['area'] = obj['area']
                single_obj['category_id'] = wordname_15.index(obj['name']) + 1
                single_obj['segmentation'] = []
                # single_obj['segmentation'].append(obj['poly'])
                single_obj['iscrowd'] = 0
                # xmin, ymin, xmax, ymax = min(obj['poly'][0::2]), min(obj['poly'][1::2]), \
                #                          max(obj['poly'][0::2]), max(obj['poly'][1::2])
                # width, height = xmax - xmin, ymax - ymin
                # single_obj['bbox'] = xmin, ymin, width, height
                single_obj['bbox'] = obj['bbox']
                single_obj['image_id'] = image_id
                single_obj['id'] = inst_count
                inst_count = inst_count + 1
                
                if detection_format:
                    single_obj['score'] = 1
                    # find id corresponding to file
                    single_obj['image_id'] = [
                        im['id']
                        for im in gtref['images']
                        if im['file_name'].split('.')[0]==os.path.basename(file).split('.')[0]
                    ][0]

                data_dict['annotations'].append(single_obj)

            image_id = image_id + 1

        if detection_format:
            data_dict = data_dict["annotations"]

        json.dump(data_dict, f_out)
        
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--is_gt', type=str, default='true', help='initial weights subpath')
    parser.add_argument('--cropsz', type=int, default=1024, help='crop size')
    parser.add_argument('--img_id_reference_coco_fn', type=str, default='', help='dataset path')
    parser.add_argument('--outputpath', type=str, default='/iqf/outputpath', help='outputpath')
    opt = parser.parse_args()
    
    cropsz = opt.cropsz
    is_gt = opt.is_gt in ['true','default','GT']
    
    # gt_path = f'/Nas/DOTA1_0/split_ss_dota1_0_glasgow_{cropsz}/val'
    gt_path = opt.img_id_reference_coco_fn
    if is_gt:
        RESULT_PATH = gt_path
    else:
        #not cropped GT but a specific cropped inference
        # inference_annots_dir = f'/Nas/DOTA1_0/split_ss_dota1_0_glasgow_{cropsz}/results/{model}'
        inference_annots_dir = opt.outputpath
        os.system(f'ln -sf {gt_path}/images {inference_annots_dir}')
        RESULT_PATH = inference_annots_dir
    
    DOTA2COCO(
        RESULT_PATH,
        os.path.join(RESULT_PATH,('coco.json' if is_gt else 'output.json')),
        is_gt = is_gt,
        fn_img_id_ref_gt = os.path.join(gt_path,'coco.json')
    )
