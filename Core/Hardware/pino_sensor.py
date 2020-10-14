#!/usr/bin/python3

import time
import adafruit_hcsr04
import board
from digitalio import DigitalInOut , Direction ,Pull
from adafruit_debouncer import Debouncer
import threading
from queue import Queue

"""
Reference
https://m.blog.naver.com/PostView.nhn?blogId=chandong83&logNo=221155355360


"""


# noinspection PyPep8Naming
class Pino_SENSOR:
    """
    A. con & deconstruct
    """
    def __init__(self):
        # 1. Static Variables
        self.MAX_DISTANCE = 150  # [cm] Max Boundary distance

        # 2. variables
        self.distance = 150   # [cm] Measured distance
        self.volume = 0     # 0 ~ 9 relative Speaker Volume
        self.last_reset_time = 0
        self.last_exception = ""
        self.sw_flag = False

        # 3. Objects
        self.sonar = None

        self.sw_queue = Queue()
        self.statue_queue = Queue()

        # 4. Init Functions
        self.t1 = threading.Thread(target=self.read_switch, args=(self.sw_queue, self.statue_queue))
        self.t1.daemon = True
        self.reset()

    def __del__(self):
        # Free GPIO
        # noinspection PyBroadException
        try:
            self.sonar.deinit()
        except :
            pass
    """
    B. reset 
    """
    def reset(self):
        # 1. check last reset time,
        #    only can reset after 1min after last reset
        if (time.time() - self.last_reset_time) < 60:
            return 0

        # 2. if self.GPIO exists..
        if self.sonar is not None:
            self.sonar.deinit()

        # 3. refresh last reset time
        self.last_reset_time = time.time()
        self.last_exception = ""

        # 4. re open GPIO
        try:
            # 4.1 init GPIO
            self.sonar = adafruit_hcsr04.HCSR04(board.D23, board.D24)
        except Exception as E:
            self.last_exception = "reset() ," +repr(E)
            return -1

    """
    C. Public Functions
    """
    # [C.1] read ultra sonic sensor, and store at "self.distance"
    def read_sonic_sensor(self):
        if not self.t1.is_alive():
            print("[Warning] pino_sensor start thread")
            if self.t1 is not None:
                del self.t1
            self.t1 = threading.Thread(target=self.read_switch, args=(self.sw_queue, self.statue_queue))
            self.t1.daemon = True
            self.t1.start()

        if self.statue_queue.qsize() < 10:
            self.statue_queue.put(1)

        while not self.sw_queue.empty():
            self.sw_flag = True
            self.sw_queue.get()
            self.volume += 1
            if self.volume > 10:
                self.volume = 0

        for i in range(10):
            try:
                self.distance = self.sonar.distance
                return self.distance
            except RuntimeError:
                time.sleep(0.05)

        return self.MAX_DISTANCE

    def read_switch(self,sw_queue,statue_queue):
        switch_pin = DigitalInOut(board.D17)
        switch_pin.direction = Direction.INPUT
        switch_pin.pull = Pull.DOWN
        switch = Debouncer(switch_pin)

        cnt  = 0
        while True:
            switch.update()
            if switch.fell:
                sw_queue.put(1)

            cnt +=1
            time.sleep(0.2)
            if cnt > 100 :
                #print("check alive, %d"%self.statue_queue.qsize())
                if statue_queue.empty():
                    break
                else :
                    statue_queue.get_nowait()
                cnt = 0

        print("[Warning] pino_sensor exit sensor thread")
        del switch
        switch_pin.deinit()
        return 0
