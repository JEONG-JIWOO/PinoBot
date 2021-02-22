#!/usr/bin/python3

"""
Description : PinoBot GPIO handling module
Author : Jiwoo Jeong
Email  : Jiwoo@gepetto.io  / jjw951215@gmail.com
Reference
https://m.blog.naver.com/PostView.nhn?blogId=chandong83&logNo=221155355360

V 1.0
    - make module and test done
    - add comment form

V 1.0.1 [WIP]
    - [X, documentation ] add Comment

"""

import RPi.GPIO
import time


class Pino_GPIO:
    def __init__(self):
        # 1. Static Variables
        self.MAX_DISTANCE = 150  # [cm] Max Boundary distance
        self.TIMEOUT = self.MAX_DISTANCE * 2 * 29.41  # [ms] sensor timeout limits
        self.SW_Pin = 17    # [GPIO17] Volume switch pin
        self.TRIG_Pin = 23  # [GPIO23] sonic sensor trigger pin
        self.ECHO_Pin = 24  # [GPIO24] sonic sensor echo pin

        # 2. variables
        self.distance = 0  # [cm] Measured distance
        self.sw_flag = False
        self.volume = 0  # 0 ~ 9 relative Speaker Volume

        # 3. Objects
        self.GPIO = RPi.GPIO
        self.GPIO.cleanup()
        self.GPIO.setmode(self.GPIO.BCM)
        # 4.2 init GPIO PINS
        self.GPIO.setup(self.SW_Pin, self.GPIO.IN, pull_up_down=self.GPIO.PUD_DOWN)
        self.GPIO.setup(self.TRIG_Pin, self.GPIO.OUT)

        self.GPIO.setup(
            self.ECHO_Pin, self.GPIO.IN, pull_up_down=self.GPIO.PUD_DOWN
        )
        # 4.3 init GPIO interrupt
        self.GPIO.add_event_detect(
            self.SW_Pin, self.GPIO.RISING, callback=self._sw_callback
        )


    def read_sonic_sensor(self):
        """
        read ultrasonic sensor and return distance
        :param

        Notes
        -----
        if error occurs, reset()

        Return
        ------
        self.distance ( float , cm )

        Example
        -------
        pg = Pino_GPIO()
        distance = pg.read_sonic_sensor()
        >> print(distance)
           11.23

        """

        # 1. send start signal to Trigger pin
        self.GPIO.output(self.TRIG_Pin, True)
        time.sleep(0.00001)
        self.GPIO.output(self.TRIG_Pin, False)

        # 2. receive response
        measure_start = time.time()
        pulse_start = 0
        pulse_end = 0

        # 3. wait for first pulse.
        while self.GPIO.input(self.ECHO_Pin) == 0:
            pulse_start = time.time()
            if ((pulse_start - measure_start) * 1000000) >= self.TIMEOUT:
                return 150

        # 4. measure time for last pulse.
        measure_start = time.time()
        while self.GPIO.input(self.ECHO_Pin) == 1:
            pulse_end = time.time()
            if ((pulse_end - pulse_start) * 1000000) >= self.TIMEOUT:
                return 150

        # 5. change time to distance
        self.distance = (pulse_end - pulse_start) * 17001  # 1000000/2 / 29.41

        return self.distance


    def _sw_callback(self, channel):
        """
        gpio switch interrupt callback function

        Notes
        -----
        if switch is on, call this fucnctions
        """
        # change sw_flag to True
        if not self.sw_flag:
            self.sw_flag = True
            # Volume Switch Interrupt Function
            # Volume changes circular 0 -> 1 -> 2 ..... -> 9 -> 0
            if self.volume > 9:
                self.volume = 0
            else:
                self.volume += 1
