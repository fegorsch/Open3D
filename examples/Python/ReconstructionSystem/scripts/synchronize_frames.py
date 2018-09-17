import math
import os
import sys
import shutil
import argparse
sys.path.append("../../Utility")
from common import *
# original code is written by Andrew. W. Chen
# input: openni style unsynchronized color and depth images
# output: synchronized color and depth images

def run_synchronization(args):
    assert len(sys.argv) == 2
    folder_path = sys.argv[1]
    depth_files = [name for name in os.listdir(os.path.join(folder_path, "depth"))
            if name.lower().endswith('.png')]
    if os.path.exists(os.path.join(folder_path, "image")):
        color_files = [name for name in os.listdir(os.path.join(folder_path, "image"))
                if name.lower().endswith('.jpg')]
    else:
        color_files = [name for name in os.listdir(os.path.join(folder_path, "rgb"))
                if name.lower().endswith('.jpg')]
    if args.debug_mode:
        print(depth_files)
        print(color_files)

    # filename format is:
    # frame-timestamp.filetype
    timestamps = {'depth':[None] * len(depth_files),
            'color':[None] * len(color_files)}
    for i, name in enumerate(depth_files):
        depth_timestamp = int(os.path.basename(depth_files[i]).replace('-','.').split('.')[1])
        timestamps['depth'][i] = depth_timestamp
    for i, name in enumerate(color_files):
        color_timestamp = int(os.path.basename(color_files[i]).replace('-','.').split('.')[1])
        timestamps['color'][i] = color_timestamp

    # associations' index is the color frame, and the value at
    # that index is the best depth frame for the color frame
    associations = []
    depth_idx = 0
    for i in range(len(color_files)):
        best_dist = float('inf')
        while depth_idx <= len(depth_files)-1 and i <= len(color_files)-1:
            dist = math.fabs(timestamps['depth'][depth_idx] - \
                    timestamps['color'][i])
            if dist > best_dist:
                break
            best_dist = dist
            depth_idx += 1
            if depth_idx > timestamps['depth'][-1]:
                print("Ended at color frame %d, depth frame %d" % (i, depth_idx))
        associations.append(depth_idx-1)
        if args.debug_mode:
            print("%d %d %d %d" % (i, depth_idx-1,
                    timestamps['depth'][depth_idx-1], timestamps['color'][i]))

    os.rename(os.path.join(folder_path, "depth"),
            os.path.join(folder_path, "temp"))
    if not os.path.exists(os.path.join(folder_path, "depth")):
        os.makedirs(os.path.join(folder_path, "depth"))
    for i, assn in enumerate(associations):
        os.rename(os.path.join(folder_path, "temp",
                os.path.basename(depth_files[assn])),
                os.path.join(folder_path, "depth/%06d.png" % (i+1)))
    shutil.rmtree(os.path.join(folder_path, "temp"))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Synchronize color and depth images")
    parser.add_argument("dataset", help="path to the dataset")
    parser.add_argument("--debug_mode", help="turn on debug mode", action="store_true")
    args = parser.parse_args()
    run_synchronization(args)
