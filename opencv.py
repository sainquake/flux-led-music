#!/usr/bin/env python3
#pip install pillow
#pip install scikit-image
#pip install opencv-python
# pip install opencv-contrib-python
#pip install kmeans
import cv2
import numpy as np
from skimage import io

import PIL.ImageGrab

im = PIL.ImageGrab.grab()
img = np.asarray(im)
average = img.mean(axis=0).mean(axis=0)
print(average)
pixels = np.float32(img.reshape(-1, 3))

n_colors = 5
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1)
flags = cv2.KMEANS_RANDOM_CENTERS

_, labels, palette = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)
_, counts = np.unique(labels, return_counts=True)

dominant = palette[np.argmax(counts)]

print(dominant)
