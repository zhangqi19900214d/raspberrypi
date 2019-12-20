#!/usr/bin/python3
#enoding=utf-8

import cv2
import numpy as np
from darkflow.net.build import TFNet
import matplotlib.pyplot as plt

#option = {'model': 'D:/CodeFile/darkflow-master/cfg/yolo.cfg',
#          'load': 'D:/CodeFile/darkflow-master/bin/yolov2.weights',
#          'thereshold': 0.1}

option = {'model': '../darknet_v2/cfg/tiny-yolov2-trial3-noBatch.cfg',
          'load': '../darknet_v2/weights_lite/tiny-yolov2-trial3-noBatch.weights',
          'labels': '../darknet_v2/data/voc.names',
          #'config': 'x64/cfg/',
          'thereshold': 0.7}

tfnet = TFNet(option)

def test_pic():
    img = cv2.imread('D://dog.jpg')
    cv2.imshow('', img)

    result = tfnet.return_predict(img)

    print(result)
    tl = (result[1]['topleft']['x'], result[1]['topleft']['y'])
    br = (result[1]['bottomright']['x'], result[1]['bottomright']['y'])

    cv2.rectangle(img, tl, br, (0, 255, 0), 7, )

    cv2.putText(img, result[1]['label'], tl, cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 2)
    plt.imshow(img)
    plt.show()

def test_video():
    cap = cv2.VideoCapture(0)
    fps = 30
    size = (1920, 1080)
    #writer = cv2.VideoWriter('dark.avi', -1, fps, size)
    colors = [tuple(255 * np.random.rand(3)) for i in range(5)]
    while (cap.isOpened()):
        ret, frame = cap.read()
        if ret:
            results = tfnet.return_predict(frame)

            for color, result in zip(colors, results):
                if result['confidence'] > 0.7:
                    print(results)
                    tl = (result['topleft']['x'], result['topleft']['y'])
                    br = (result['bottomright']['x'], result['bottomright']['y'])
                    label = result['label']
                    cv2.rectangle(frame, tl, br, color, 7, )
                    cv2.putText(frame, label, tl, cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 2)
            #writer.write(frame)
            cv2.imshow('frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            cap.release()
            cv2.destroyAllWindows()
            break

if '__main__' == __name__:
    test_video()
