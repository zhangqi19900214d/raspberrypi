#!/usr/bin/python3
#encoding=utf-8

import cv2
import time
import numpy as np

if __name__ == '__main__':
    video = cv2.VideoCapture(0)
    while True:
        _, frame = video.read();
        if (_):
            cv2.imshow("track", frame)
            k = cv2.waitKey(30) & 0xff
            if k == 27:
                break
