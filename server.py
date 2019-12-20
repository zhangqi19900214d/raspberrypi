#!/usr/bin/python3
#encoding=utf-8

import cv2
import numpy as np
import tornado
import tornado.ioloop
import tornado.web
import base64
import json
import numpy
import time

import numpy as np
from darkflow.net.build import TFNet
import matplotlib.pyplot as plt


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, numpy.integer):
            return int(obj)
        elif isinstance(obj, numpy.floating):
            return float(obj)
        elif isinstance(obj, numpy.ndarray):
            return obj.tolist()
        else:
            return super(MyEncoder, self).default(obj)

option = {'model': '../darknet_v2/cfg/tiny-yolov2-trial3-noBatch.cfg',
          'load': '../darknet_v2/weights_lite/tiny-yolov2-trial3-noBatch.weights',
          'labels': '../darknet_v2/data/voc.names',
          #'config': 'x64/cfg/',
          'thereshold': 0.7}

tfnet = TFNet(option)

class MainHandler(tornado.web.RequestHandler):


    def initialize (self):
        #option = {'model': 'D:/CodeFile/darkflow-master/cfg/yolo.cfg',
        #          'load': 'D:/CodeFile/darkflow-master/bin/yolov2.weights',
        #          'thereshold': 0.1}

        #option = {'model': '../darknet_v2/cfg/tiny-yolov2-trial3-noBatch.cfg',
        #          'load': '../darknet_v2/weights_lite/tiny-yolov2-trial3-noBatch.weights',
        #          'labels': '../darknet_v2/data/voc.names',
        #          #'config': 'x64/cfg/',
        #          'thereshold': 0.7}
        #self.face_haar = cv2.CascadeClassifier("./data/haarcascades/haarcascade_frontalface_default.xml")
        #self.__tfnet = TFNet(option)

        print("server init success...")

    def get(self):
        self.write("Hello, world")

    def post(self):
        print(self.request.path)
        print(self.request.remote_ip)
        #print(self.request.body)
        print(self.request.headers)

        image, t= self.decode_image()

        start_time = time.time()
        res = self.handle_with_yolo(image)
        cost = time.time() -start_time

        res['detect_cost'] = str(cost)
        print('predict cost %fms' % cost)

        self.write(json.dumps(res, cls=MyEncoder))

    def handle_with_haar(self):
        gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        faces = self.face_haar.detectMultiScale(gray_img, 1.3, 1)
        res = {'status':False}

        for face_x, face_y, face_w, face_h in faces:
            cv2.rectangle(image, (face_x, face_y), (face_x+face_w, face_y+face_h), (0, 255, 0), 2)
            res = {'status':'success', 'face_x':face_x, 'face_y':face_y, 'face_w':face_w, 'face_h':face_h}

        #self.write(json.dumps(res, cls=MyEncoder))

        #cv2.imshow('', image)
        #cv2.waitKey(30)

        return res

    def handle_with_yolo(self, frame):

        #results = self.__tfnet.return_predict(frame)
        results = tfnet.return_predict(frame)

        colors = [tuple(255 * np.random.rand(3)) for i in range(5)]
        max_confidence = 0.0

        x, y, w, h, = 0, 0, 0, 0
        for color, result in zip(colors, results):
            if result['confidence'] > max_confidence:
                tl = (result['topleft']['x'], result['topleft']['y'])
                br = (result['bottomright']['x'], result['bottomright']['y'])
                label = result['label']

                x, y = result['topleft']['x'], result['topleft']['y']
                w, h = result['bottomright']['x'] - x, result['bottomright']['y'] - y

                max_confidence = result['confidence'] 

                #cv2.rectangle(frame, tl, br, color, 7, )
                #cv2.putText(frame, label, tl, cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 2)

        res = {'status':"false"}

        if max_confidence > 0.5:
            res['status'] = "success"
            res['x'] = x
            res['y'] = y
            res['w'] = w
            res['h'] = h
            res['label'] = label
            res['confidence'] = max_confidence

        return res

    def decode_image(self):

        body = eval(self.request.body)
        image = body['image']
        upload_time = float(body['upload_time'])

        time_now = time.time()
        print('recv image cost ', time_now - upload_time)

        image = image.encode('ascii')
        image = base64.b64decode(image)
        image = np.frombuffer(image, np.uint8)
        frame = cv2.imdecode(image, cv2.COLOR_RGB2BGR)
        print(frame.shape)
        return frame, time

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()

