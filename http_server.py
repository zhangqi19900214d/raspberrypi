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
import time
import threading

try:
    import RPi.GPIO as GPIO
except Exception as e:
    class GPIO():
        OUT=0
        LOW=0
        HIGH=0

        @staticmethod
        def setup(x, y):
            pass

        @staticmethod
        def output(x, y):
            pass

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

class Wheel():
    def __init__(self, gpio_1, gpio_2):
        self.__gpio_1 = gpio_1
        self.__gpio_2 = gpio_2

        GPIO.setup(self.__gpio_1, GPIO.OUT)
        GPIO.setup(self.__gpio_2, GPIO.OUT)

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

class Car:
    def __init__(self, gpio, wheelNo=None):

        if isinstance(wheelNo, int):
            if len(gpio) != 1:
                print('gpio size is not 1')
            else:
                self.__wheels = [None, None, None, None]
                self.__wheels[wheelNo] = Wheel(gpio[0][0], gpio[0][1])
        else:
            if len(gpio) != 4:
                print('gpio size is not 4')
            else:
                self.__wheel_1 = Wheel(gpio[0][0], gpio[0][1])
                self.__wheel_2 = Wheel(gpio[1][0], gpio[1][1])
                self.__wheel_3 = Wheel(gpio[2][0], gpio[2][1])
                self.__wheel_4 = Wheel(gpio[3][0], gpio[3][1])

                self.__wheels = [self.__wheel_1, self.__wheel_2, self.__wheel_3, self.__wheel_4]

    def stop(self, wheelNo = None):
        if isinstance(wheelNo, int):
            [w.stop() for w in self.__wheels]
        else:
            self.__wheels[wheelNo].stop()

    def forward(self, wheelNo = None):
        if isinstance(wheelNo, int):
            self.__wheels[wheelNo].forward()
        else:
            [w.forward() for w in self.__wheels]

    def backward(self, wheelNo = None):
        if isinstance(wheelNo, int):
            self.__wheels[wheelNo].backward()
        else:
            [w.backward() for w in self.__wheels]

    def turn_left(self):
        pass

    def turn_right(self):
        pass


class MainHandler(tornado.web.RequestHandler):
    cmd_stop = 0
    cmd_test = 1

    __Wheel = [None, None, None, None]

    def initialize (self):
        #print("server init success...")
        pass

    def get(self):
        self.write("Hello, world")

    def post(self):
        #print(self.request.path)
        #print(self.request.remote_ip)
        #print(self.request.body)
        #print(self.request.headers)

        request = eval(self.request.body)
        cmd = request['command']
        message = request['message']

        if cmd == MainHandler.cmd_stop:
            pass
        elif cmd == MainHandler.cmd_test:
            self.test_wheel(message)

    def get_command(self):
        request = eval(self.request.body)
        return request['command']

    def test_wheel(self, message):
        wheelNo = message['wheelNO']
        gpio = [(message['gpio1'], message['gpio2'])]

        print('test wheel %d as %s' % (wheelNo, gpio))
        _car = Car(gpio, wheelNo)
        _car.forward(wheelNo)

def make_app():
    return tornado.web.Application([
        (r"/car/control", MainHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(9000)
    tornado.ioloop.IOLoop.current().start()

