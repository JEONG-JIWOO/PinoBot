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

from Hardware.SPI import apa_102
from Hardware.GPIO import switch
from Hardware.I2C import pca_9685, lcd_1602

#from queue import Queue
# spi, i2c raspi-config

class HardwareV1():
    def __init__(self):

        self.set_logger()
        self.SW = switch.Switch("GPIO17")
        self.LED = apa_102.APA102(num_led=2)
        self.LCD = lcd_1602.LCD1602(0x27)
        self.SERVO = pca_9685.PCA9685(0x20)
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
        self.log = logging.getLogger("Hardware_V1")
        self.log.setLevel(logging.DEBUG)
        formatter = logging.Formatter('[%(levelname)s] (%(asctime)s : %(filename)s:%(lineno)d) > %(message)s')

        # 2.2 set file logger 
        self.log_file = logging.FileHandler(filename = '/home/pi/pinobot/log/HardwareV1.log', 
                                            mode='w',
                                            encoding='utf-8')
        self.log_file.setFormatter(formatter)
        self.log.addHandler(self.log_file)

        # 2.3 set consol logger
        self.log_consol = logging.StreamHandler()
        self.log_consol.setFormatter(formatter)
        self.log.addHandler(self.log_consol)

        # 2.4 logger Done.
        self.log.info("Start Hardware Module")

    def write(self, text ="", led = [], servo = []):
        
        if text != "":
            self.log.info("LCD SHOW text %s"%text )
            self.LCD.send_msg(text)
        
        if len(led) == 3:
            self.setLED(0,led)
            self.setLED(1,led)

        if len(led) == 6:
            self.setLED(0,led[0:3])
            self.setLED(1,led[3:6])

        if len(servo) == 3:
            pass

    def read(self):
        return (self.SW.read_once())
        
        