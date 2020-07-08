#!/usr/bin/env python3.7

"""
Hardware v1 control module

based on gpiozero lib


wiring : 

SW0 [ONBOARD] :GPIO17
SW1 [EXTERNAL] : GPIO12 OR GPIO13

APA102 RGB LED : SPI interface, 

I2C-1 : Address[] : PCA9685 PWM MODULE
I2C-1 : Address[] : character LCD module

"""
import logging

from Hardware.I2C import servo
from Hardware.SPI import apa_102
from Hardware import PinoGPIO , PinoUart

#from queue import Queue
# spi, i2c raspi-config

class HardwareV1():
    def __init__(self):
        # 1. Static Variables

        # 2. variables

        # 3. Objects

        # 3.1 logs
        self.log = self.set_logger()

        self.SERVO = servo.SERVO()

        self.LED = apa_102.APA102(num_led=2)

        self.GPIO = PinoGPIO.Pino_GPIO()

        self.UART = PinoUart.Pino_UART(port= "COM0", baud_rate = 115200)

        self.setLED(0,[0,0,0])
        self.setLED(1,[0,0,0])

    def __del__(self):
        self.setLED(0,[0,0,0])
        self.setLED(1,[0,0,0])
        self.LED.cleanup()

    def setLED(self, i, colors):
        self.LED.set_pixel(i, int(colors[0]), int(colors[1]), int(colors[2]))
        self.LED.show()
    


    """
    A.1 Initializing Logger
    """
    def set_logger(self):
        # 2.1 set logger and formatter
        log = logging.getLogger("Hardware_V1")
        log.setLevel(logging.DEBUG)
        formatter = logging.Formatter('[%(levelname)s] (%(asctime)s : %(filename)s:%(lineno)d) > %(message)s')

        # 2.2 set file logger 
        log_file = logging.FileHandler(filename = '/home/pi/Desktop/PinoBot/log/HardwareV1.log',
                                            mode='w',
                                            encoding='utf-8')
        log_file.setFormatter(formatter)
        log.addHandler(log_file)

        # 2.3 set consol logger
        log_consol = logging.StreamHandler()
        log_consol.setFormatter(formatter)
        log.addHandler(log_consol)

        # 2.4 logger Done.
        log.info("Start Hardware Module")
        return log

    def write(self, text ="", led = [], servo = []):
        
        if text != "":
            #self.log.info("LCD SHOW text %s"%text )
            self.LCD.send_msg(text)
        
        if len(led) == 3:
            self.setLED(0,led)
            self.setLED(1,led)

        if len(led) == 6:
            self.setLED(0,led[0:3])
            self.setLED(1,led[3:6])

        if len(servo) == 2:
            self.SERVO.send_angles(servo[0],servo[1])

        elif len(servo) == 3:
            self.SERVO.send_angles(8 ,servo[0])
            self.SERVO.send_angles(9, servo[1])
            self.SERVO.send_angles(10, servo[2])

    def read_sw(self):
        return (self.SW.read_once())
    
    def read_sonic(self):
        return (self.SonicSensor.measure_once())
        