#!/usr/bin/python3
#encoding=utf-8

import tornado
import tornado.ioloop
import tornado.web
import base64
import time
import threading

try:
    import RPi.GPIO as _GPIO
except Exception as e:
    class _GPIO():
        OUT=0
        LOW=0
        HIGH=0
        BOARD=0

        @staticmethod
        def setup(index, inout):
            pass

        @staticmethod
        def output(index, high):
            pass

        @staticmethod
        def setmode(x):
            pass

finally:
    _GPIO.setmode(_GPIO.BOARD)
    _GPIO.setmode(_GPIO.BOARD)

class GPIO():
    def __init__(self, index):
        self.__index = index

    def setup(self, inout = _GPIO.OUT):
        _GPIO.setup(self.__index, inout)

    def high(self):
        _GPIO.output(self.__index, _GPIO.HIGH)
        #print("%d set high" % self.__index)
        pass

    def low(self):
        _GPIO.output(self.__index, _GPIO.LOW)
        #print("%d set low" % self.__index)
        pass

    def __del__(self):
        #_GPIO.cleanup()
        pass


class Wheel():
    def __init__(self, io1, io2):
        self.__io1 = GPIO(io1)
        self.__io2 = GPIO(io2)

        self.__io1.setup()
        self.__io2.setup()

        self.run_period = time.time()

        th = threading.Thread(target = Wheel.running, args = [self,])
        th.start()

    def __del__(self):
        self.__io1.low()
        self.__io2.low()

    def backward(self, term):
        self.__io1.high()
        self.__io2.low()
        self.run_period = time.time() + term

    def forward(self, term):
        self.__io2.high()
        self.__io1.low()
        self.run_period = time.time() + term
        print("will run %dms" % (self.run_period-time.time()))

    def stop(self):
        self.__io1.low()
        self.__io2.low()
        #print("wheel stop...")
    
    @staticmethod
    def running(this):
        while True:

            if time.time() >= this.run_period:
                this.stop()
            else:
                time.sleep(0.1)

class Car:
    def __init__(self):
        self.__wheels = [None, None, None, None]

    def __del__(self):
        for wheel in self.__wheels:
            if isinstance(wheel, Wheel):
                wheel.stop()

    def set_wheel(self, index, io1, io2):
        self.__wheels[index] = Wheel(io1, io2)

    def stop(self, wheel_index = -1):
        if wheel_index != -1:
            [w.stop() for w in self.__wheels]
        else:
            self.__wheels[wheel_index].stop()

    def forward(self, term, wheel_index = -1):
        if wheel_index != -1:
            self.__wheels[wheel_index].forward(term)
        else:
            [w.forward(term) for w in self.__wheels]

    def backward(self, term, wheel_index = -1):
        if wheel_index != -1:
            self.__wheels[wheel_index].backward(twem)
        else:
            [w.backward(term) for w in self.__wheels]

    def turn_left(self):
        pass

    def turn_right(self):
        pass


class DriverService(tornado.web.RequestHandler):
    __car = Car()
    __car.set_wheel(0, 29, 31)
    __car.set_wheel(1, 13, 15)
    __car.set_wheel(2, 11, 12)
    __car.set_wheel(3, 32, 33)

    def get(self):

        if self.request.path == '/':
            self.request.path = '/index.html'

        path = './' + self.request.path
        with open(path, 'r') as fp:
            text = fp.read()
            self.write(text)

    def post(self):
        #print(self.request.path)
        #print(self.request.remote_ip)
        #print(self.request.body)
        #print(self.request.headers)

        request = eval(self.request.body)
        cmd = request['command']
        message = request['message']
        print(request)

        if cmd == 0:
            self.stop(message)
            print("recv stop...")
        elif cmd == 1:
            self.test_wheel(message)

    def get_command(self):
        request = eval(self.request.body)
        return request['command']

    def stop(self, message):
        wheel_index = message['wheelNO']
        DriverService.__car.stop(wheel_index)

    def test_wheel(self, message):
        term = message['term']
        wheel_index = message['wheelNO']
        io1, io2 = (message['gpio1'], message['gpio2'])

        #DriverService.__car.set_wheel(wheel_index, io1, io2)
        DriverService.__car.forward(term, wheel_index)

def make_app():
    return tornado.web.Application([
        (r"/car/control", DriverService),
        (r"/", DriverService),
        (r"/index.html", DriverService),
        (r"/my.html", DriverService),

    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(9000)
    tornado.ioloop.IOLoop.current().start()

