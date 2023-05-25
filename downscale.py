import os
from PIL import Image
import os
import cv2
import numpy as np
import shutil
import time
import argparse
import sys
begin=time.time()
parser= argparse.ArgumentParser(description='downscaleprep')
parser.add_argument('--scale',
                       metavar='scale',
                       type=int,
                       default=32,
                       help='scale tuple')
parser.add_argument('--subtomogram_path',
                       metavar='subtomogram_path',
                       type=str,
                       default="./subtomogram_png/",
                       help='the path to subtomogram image')
parser.add_argument('--resultfolder',
                       metavar='resultfolder',
                       type=str,
                       default="./result/",
                       help='results stored here')
args = parser.parse_args()

subtomogram_path=args.subtomogram_path
resultfolder=args.resultfolder
scale=args.scale

scaletuple=(scale,scale)

tempfolder1="./temp1/"
temp_sliced_subtomogram="./temps/"

for folder in [resultfolder,tempfolder1,temp_sliced_subtomogram]:
    if os.path.exists(folder):
        shutil.rmtree(folder)
    os.makedirs(folder)

subtomogram_list = [name for name in os.listdir(subtomogram_path) if name.endswith('.png')]
n=len(subtomogram_list)

def norm_img(img):
    max_v = img.max()
    min_v = img.min()
    img = (img - min_v) / (max_v - min_v)
    return img*255

def convert_to_8bit(path,filename,destination):
    img_copy=cv2.imread(path,cv2.IMREAD_ANYDEPTH)
    img_copy=norm_img(img_copy)
    cv2.imwrite(destination+filename,img_copy)

def slicer_scaler(path,destination,scale):
    img = Image.open(path)
    global mark
    for i in range(5):
        for j in range(6):
            region = img.crop((j*33, i*33, j*33 + 33, i*33 + 33))
            region = region.crop((0,0,32,32))
            region = region.convert('L')
            region = region.resize(scale)
            region.save(os.path.join(destination,str(mark)+".png"))
            mark = mark + 1
    img.close()


mark=0
print("Converting and slicing subtomograms..")
for image in subtomogram_list:
    try:
        convert_to_8bit(subtomogram_path+image,image,tempfolder1)
    except AttributeError:
        sys.exit("Invalid path!")
    slicer_scaler(tempfolder1+image,temp_sliced_subtomogram,scaletuple)

for tempdir in [temp_sliced_subtomogram,tempfolder1]:
    shutil.rmtree(tempdir)

print(f"Success. Executed in {time.time()-begin} seconds")