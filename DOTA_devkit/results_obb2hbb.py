import dota_utils as util
import os

import argparse

def mybasename(fullname):
    return os.path.basename(os.path.splitext(fullname)[0])

def OBB2HBB(srcpath, dstpath):
    filenames = util.GetFileFromThisRootDir(srcpath)
    if not os.path.exists(dstpath):
        os.makedirs(dstpath)
    for file in filenames:
        with open(file, 'r') as f_in:
            with open(os.path.join(dstpath, mybasename(file) + '.txt'), 'w') as f_out:
                lines = f_in.readlines()
                splitlines = [x.strip().split() for x in lines]
                for index, splitline in enumerate(splitlines):
                    label = splitline[8]
                    poly = splitline[:8]
                    poly = list(map(float, poly))
                    xmin, xmax, ymin, ymax = min(poly[0::2]), max(poly[0::2]), min(poly[1::2]), max(poly[1::2])
                    rec_poly = [xmin, ymin, xmax, ymax]
                    outline = ' '.join(map(str, rec_poly))+ ' '+ label
                    if index != (len(splitlines) - 1):
                        outline = outline + '\n'
                    f_out.write(outline)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Train a detector')
    parser.add_argument(r'--obbdir', default=r'obbdir')
    parser.add_argument(r'--hbbdir', default=r'hbbdir')
    args = parser.parse_args()
    OBB2HBB(args.obbdir, args.hbbdir)