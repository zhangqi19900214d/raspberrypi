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


def main():

    car = Car()
    car.launch()
    car.stop()
    car.turn_left()
    #car.turn_right()
    #time.sleep(10)
    #return

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print("catch an exception as %s" % e)
    finally:
        GPIO.cleanup()
        car.release()
