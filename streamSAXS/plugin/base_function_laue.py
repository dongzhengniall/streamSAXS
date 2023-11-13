# -*- coding: utf-8 -*-
# defined functions for data process, independent of frame

#%%
# generic lib

import numpy as np
import h5py
#import hdf5plugin
from skimage.measure import label, regionprops
#import matplotlib.pyplot as plt

#########peak_num####################
def Find_peaks(data, picture_number, areaLimit, threshold):
    data[np.where(data > 10000)] = 0
    threshold = data.max() * 0.15
    # Thresolding img and Binarize it
    print(data)
    bw = np.where(data > threshold, 255, 0)
    # Connectivity Detection
    label_image = label(bw)
    # Blobs Properties
    props = regionprops(label_image)
    # Number of blobs
    num_blobs = len(props)
    for blob in props:
        if blob.area < areaLimit:
            num_blobs = num_blobs - 1
        else:
            continue
    return num_blobs

    #print('number of candidate peaks is', num_blobs)
    # plt.imshow(label_image)