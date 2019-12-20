#!/usr/bin/python3
# encoding=utf-8

import time
from threading import Thread
from queue import Queue
import base64
import requests
import json
import numpy as np
import cv2
import RPi.GPIO as GPIO
import time
import threading
import numpy as np
import matplotlib.pyplot as plt

GPIO.setmode(GPIO.BOARD)
GPIO.setmode(GPIO.BOARD)

class Const(object):
    class ConsError(TypeError):
        pass

    class ConstCaseError(ConsError):
        pass

    def __setattr__(self, name, value):
        if name in self.__dict__:
            raise (self.ConsError, "Can't change const.%s" % name)
        if not name.isupper():
            raise (self.ConstCaseError, "const name '%s' is not all uppercase" % name)
        self.__dict__[name] = value


const = Const()

const.SPEED0 = 0
const.SPEED1 = 1
const.SPEED2 = 2
const.SPEED3 = 3
const.SPEED4 = 4
const.SPEED5 = 5
const.MAX_SPEED = 6

const.DIRECTION_FORWARD = 1
const.DIRECTION_BACKWARD = 2

class Wheel(threading.Thread):
    def __init__(self, gpio_1, gpio_2, speed, index):
        super().__init__()
        self.__index = index
        self.__speed = speed
        self.__direction = const.DIRECTION_FORWARD
        self.__mutex = threading.Lock()
        self.__gpio_1 = gpio_1
        self.__gpio_2 = gpio_2

        GPIO.setup(self.__gpio_1, GPIO.OUT)
        GPIO.setup(self.__gpio_2, GPIO.OUT)

    def set_speed(self, speed, direction=const.DIRECTION_FORWARD):
        self.__mutex.acquire()
        self.__speed = speed
        self.__direction = direction
        self.__mutex.release()

    def backward(self):
        # set io
        GPIO.output(self.__gpio_1, GPIO.HIGH)
        GPIO.output(self.__gpio_2, GPIO.LOW)

    def forward(self):
        GPIO.output(self.__gpio_1, GPIO.LOW)
        GPIO.output(self.__gpio_2, GPIO.HIGH)

    def stop(self):
        GPIO.output(self.__gpio_1, GPIO.HIGH)
        GPIO.output(self.__gpio_2, GPIO.HIGH)

    def run_speed(self, step=100.0):
        self.__mutex.acquire()

        if self.__direction == const.DIRECTION_FORWARD:
            self.forward()
        else:
            self.backward()

        self.__mutex.release()

        sleep_time = self.__speed / step
        time.sleep(sleep_time)

        self.stop()

        sleep_time = (const.MAX_SPEED - self.__speed) / step
        time.sleep(sleep_time)

    def run(self):
        try:
            while True:
                if self.__speed > const.SPEED0:
                    self.run_speed()
                else:
                    self.stop()
                    pass

        except Exception as e:
            print('catch an exception as %s' % e)


class Car:
    def __init__(self):

        wheel_1 = Wheel(29, 31, const.SPEED0, 1)
        wheel_2 = Wheel(13, 15, const.SPEED0, 2)
        wheel_3 = Wheel(11, 12, const.SPEED0, 3)
        wheel_4 = Wheel(32, 33, const.SPEED0, 4)

        self.__wheel_1 = wheel_1
        self.__wheel_2 = wheel_2
        self.__wheel_3 = wheel_3
        self.__wheel_4 = wheel_4

        self.__wheels = [self.__wheel_1, self.__wheel_2, self.__wheel_3, self.__wheel_4]

    def launch(self):
        [w.start() for w in self.__wheels]

    def stop(self):
        [w.set_speed(const.SPEED0, const.SPEED0) for w in self.__wheels]

    def forward(self, speed):
        [w.set_speed(speed, const.DIRECTION_FORWARD) for w in self.__wheels]

    def backward(self, speed):
        [w.set_speed(speed, const.DIRECTION_BACKWARD) for w in self.__wheels]

    def turn_left(self):
        self.stop()
        self.__wheel_1.set_speed(const.SPEED4, const.DIRECTION_BACKWARD)
        self.__wheel_3.set_speed(const.SPEED3, const.DIRECTION_BACKWARD)

        self.__wheel_2.set_speed(const.SPEED3, const.DIRECTION_FORWARD)
        self.__wheel_4.set_speed(const.SPEED4, const.DIRECTION_FORWARD)

    def turn_right(self):
        self.stop()
        self.__wheel_1.set_speed(const.SPEED5, const.DIRECTION_FORWARD)
        self.__wheel_3.set_speed(const.SPEED4, const.DIRECTION_FORWARD)

        self.__wheel_2.set_speed(const.SPEED4, const.DIRECTION_BACKWARD)
        self.__wheel_4.set_speed(const.SPEED4, const.DIRECTION_BACKWARD)


class YoloDector():
        pass

class YoloDector():
    def __init__(self):
        option = {'model':  '../darknet_v2/cfg/tiny-yolov2-trial3-noBatch.cfg',
                  'load':   '../darknet_v2/weights_lite/tiny-yolov2-trial3-noBatch.weights',
                  'labels': '../darknet_v2/data/voc.names',
                  'thereshold': 0.7}

        self.__tfnet = TFNet(option)

    def detect(self, frame):

        results = self.__tfnet.return_predict(frame)

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

                cv2.rectangle(frame, tl, br, color, 7, )
                cv2.putText(frame, label, tl, cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 2)

        return frame

class RpcDector():
    def __init__(self):
        pass

    def detect(self, img_str):
        #img_str = cv2.imencode('.jpg', image)[1].tostring()
        #img_str = base64.b64encode(img_str).decode('ascii')

        upload_time = time.time()
        #url = 'http://127.0.0.1:8888/'
        url = 'http://192.168.1.109:8888/'
        data = {'image': img_str,'upload_time':str(time.time())}
        json_mod = json.dumps(data)

        res = requests.post(url=url, data=json_mod)
        print('preedict cost ', time.time() - upload_time)

        return eval(res.text)

        #{"status": true, "x": 32, "y": 103, "w": 359, "h": 376, "label": "person", "cost": "0.5026454925537109"}
        #status = res['status']
        #if status == 'success':
        #    cv2.rectangle(image, (res['x'], res['y']),(res['x'] + res['w'], res['y'] + res['h']),( 255, 0, 0), 2)


mtx = threading.Lock()
queue = Queue(2)
cap = cv2.VideoCapture(0)  # 默认的摄像头

def capture_video():#queue):#, mtx):
    width = 320
    height = 240

    #cap.set(cv2.CV_CAP_PROP_FRAME_WIDTH, width) #设置分辨率
    #cap.set(cv2.CV_CAP_PROP_FRAME_HEIGHT, height)
    cap.set(3, width) #设置分辨率
    cap.set(4, height)

    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            mtx.acquire()
            if queue.full():
                #print("queue if full...")
                queue.get();

            img_str = cv2.imencode('.jpg', frame)[1].tostring()
            img_str = base64.b64encode(img_str).decode('ascii')

            queue.put({'image':img_str, 'time':time.time()})

            #print('after input, queue.size=%d' % queue.qsize())
            mtx.release()

    print("catpure has been closed...")

def main():

    car = Car()
    car.launch()
    car.stop()
    #car.turn_left()
    #car.turn_right()
    #time.sleep(10)
    #return

    #dector = YoloDector()
    dector = RpcDector()

    #mtx = threading.Lock()
    #queue = Queue(10)

    capture_thread = threading.Thread(target = capture_video)#, args = (queue))#, mtx))
    capture_thread.start()

    last_time = time.time() + 2
    car_status = 2

    last_not_found_time = time.time()
    while True:
        mtx.acquire()
        if queue.empty():
            #print("quque is empty...")
            mtx.release()
            continue
        else:
            image_info = queue.get()
            mtx.release()

        time_now = time.time()

        frame = image_info['image'].encode('ascii')
        frame = base64.b64decode(frame)
        frame = np.frombuffer(frame, np.uint8)
        frame = cv2.imdecode(frame, cv2.COLOR_RGB2BGR)

        if True:#time_now - last_time > 0.5:# and (car_status > 1 or time_now - last_time > 4):
            res = dector.detect(image_info['image'])
            height, width = frame.shape[:2]
            print('time now=%.0f, image time=%.0f, res=%s' % (time.time(), image_info['time'], res))

            #{"status": true, "x": 32, "y": 103, "w": 359, "h": 376, "label": "person", "cost": "0.5026454925537109"}
            if res['status'] == 'success' and res['label'] == 'person':
                cv2.rectangle(frame, (res['x'], res['y']),(res['x'] + res['w'], res['y'] + res['h']),( 255, 0, 0), 2)
                w1 = res['x']
                w2 = width - res['x'] - res['w']

                h1 = res['y']
                h2 = height - res['y'] - res['h']

                print(w1, w2, h1, h2)
                if w1 > w2 * 3: #right
                    print('turn right....')
                    car_status = 0
                elif w2 > w1 * 3: #left
                    print('turn left....')
                    car_status = 1
                elif h1 > 10:# foward
                    print('forward...')
                    car_status = 2
                elif h2 < 20: #backward
                    print('backward...')
                    car_status = 3
                else:
                    print('stop...')
                    car_status = 4
                print('car status ', car_status)
                last_not_found_time = time.time()

            else:
                car_status = 4
                if time.time() - last_not_found_time > 5:
                    print('not found body in 5s')
                    car_status = int(time.time()) % 4

            last_time = time.time()

        if car_status == 0:
            car.turn_right()
        elif car_status == 1:
            car.turn_left()
        elif car_status == 2:
            car.forward(const.SPEED5)
        elif car_status == 3:
            car.backward(const.SPEED5)
        elif car_status == 4:
            car.stop()

        cv2.imshow('', frame)
        cv2.waitKey(10)

    #car.forward(const.SPEED5)
    #car.turn_left()
    #car.backward(const.SPEED5)
    #time.sleep(2)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print("catch an exception as %s" % e)
    finally:
        GPIO.cleanup()
        cap.release()
