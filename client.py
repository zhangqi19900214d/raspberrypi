#!/usr/bin/python3
#encoding=utf-8

import socket
import time
import requests
import json
import numpy as np
import cv2
import base64
'''
image = cv2.imread('./person.jpg')

img_str = cv2.imencode('.jpg', image)[1].tostring()
img_str = base64.b64encode(img_str).decode('ascii')

url = 'http://127.0.0.1:8888/'
data = {'image': img_str, 'type': '0', 'useAntiSpoofing': '0', 'time':int(time.time())}
json_mod = json.dumps(data)
res = requests.post(url=url, data=json_mod)
print(res.text)
'''
#import socket
# 创建socket对象
#sock = socket.socket()
# 连接远程主机
#sock.connect(('127.0.0.1', 8888))    # ①
#print('--%s--' % s.recv(1024).decode('utf-8'))
#s.close()


cap = cv2.VideoCapture(0)  # 默认的摄像头
# 指定视频代码
#fourcc = cv2.VideoWriter_fourcc(*"DIVX")
#out = cv2.VideoWriter('xieyang.avi', fourcc, 20.0, (640,480))
last_time = time.time() + 4

cap.set(3, 320) #设置分辨率
cap.set(4, 240)

fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi',fourcc, 20.0, (240, 320))
out = cv2.VideoWriter('output.avi', cv2.VideoWriter_fourcc('I', '4', '2', '0'), 20, (240, 320))


while(cap.isOpened()):
    ret, image = cap.read()
    time_now = time.time()

    if ret and time_now - last_time > 0.3:
        img_str = cv2.imencode('.jpg', image)[1].tostring()
        img_str = base64.b64encode(img_str).decode('ascii')

        upload_time = time.time()
        url = 'http://127.0.0.1:8888/'
        #url = 'http://192.168.1.109:8888/'
        data = {'image': img_str,'upload_time':str(time.time())}
        json_mod = json.dumps(data)

        res = requests.post(url=url, data=json_mod)
        print(res.text)
        res = eval(res.text)

        print('preedict cost ', time.time() - upload_time)

        #{"status": true, "x": 32, "y": 103, "w": 359, "h": 376, "label": "person", "cost": "0.5026454925537109"}
        status = res['status']
        if status == 'success':
            cv2.rectangle(image, (res['x'], res['y']),(res['x'] + res['w'], res['y'] + res['h']),( 255, 0, 0), 2)
        #    #cv2.imwrite('%d.jpg' % time_now, image)
            out.write(image)

        cv2.imshow('', image)
        cv2.waitKey(30)

        #if res['status'] == 'success':
        #    face_x = res['face_x']
        #    face_y = res['face_y']
        #    face_w = res['face_w']
        #    face_h = res['face_h']

        #    cv2.rectangle(image, (face_x, face_y),(face_x + face_w, face_y + face_h),( 255, 0, 0), 2)
        #    cv2.imwrite('%d.jpg' % time_now, image)

        last_time = time.time()

out.release()
#cap.rele#ase()
#cv2.dest#royAllWindows()
