#!/usr/bin/env python3.7

"""
Hardware v1 control module
based on gpiozero lib

wiring : 

SW0 [ONBOARD] :GPIO17
APA102 RGB LED : SPI interface, 

I2C-1 : Address[] : PCA9685 PWM MODULE
I2C-1 : Address[] : character LCD module

"""
import logging , time
import busio
import board

from Core.Hardware.I2C import servo , oled
from Core.Hardware import pino_gpio , pino_uart
from Core.Hardware.SPI import rgb_led


class HardwareV1:
    """
    A. con & deconstruct
    """
    def __init__(self,ini):
        # 0. Argument
        self.ini = ini

        # 1. Static Variables

        # 2. variables
        self.last_reset_time = 0
        self.last_exception = ""

        # 3. Objects
        self.I2C_BUS = None
        self.SERVO = None
        self.OLED = None
        self.SPI_BUS = None
        self.RGB_LED = None
        self.SENSOR = None
        self.UART = None
        self.log = None

        # 4. Init Functions
        self.reset()
        self.__set_default()


    def __del__(self):
        for sub_modules in [self.SERVO, self.OLED , self.RGB_LED , self.SENSOR, self.I2C_BUS, self.SPI_BUS]:
            if sub_modules is not None:
                try:
                    del sub_modules
                except Exception as E:
                    self.log.warning("HardwareV1.del()," + repr(E))

    """
    B. reset 
    """
    def reset(self):
        # 1. check last reset time,
        #    only can reset after 1min after last reset
        if (time.time() - self.last_reset_time) < 60:
            return 0

        # 2. if object exists..
        for sub_modules in [self.SERVO, self.OLED , self.RGB_LED , self.SENSOR, self.I2C_BUS, self.SPI_BUS]:
            if sub_modules is not None:
                try:
                    del sub_modules
                except Exception as E:
                    self.log.warning("HardwareV1.reset(), #2. del " + repr(E))

        # 3. refresh last reset time
        self.last_reset_time = time.time()

        # 4. re open GPIO
        try:
            # 4.1 init I2C
            from board import SCL, SDA
            self.I2C_BUS = busio.I2C(SCL, SDA)
            self.OLED = oled.OLED(self.I2C_BUS)
            self.OLED.send_console(1,"Hardware init...   ")

            self.SERVO = servo.SERVO(self.I2C_BUS)
            time.sleep(0.3)
            # 4.2 init SPI
            self.SPI_BUS = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
            self.RGB_LED = rgb_led.RGB_LED(self.SPI_BUS)

            # 4.3 init GPIO
            self.SENSOR = pino_gpio.Pino_GPIO()
            self.OLED.send_console(2,"Hardware init...  \n" +
                                     "Hardware reset..    ")

            # 4.4 init Serial
            self.UART = pino_uart.Pino_UART()

            # 4.5 init log
            self.log = self.__set_logger()
            time.sleep(0.3)

        except Exception as E:
            self.log.warning("HardwareV1.reset() , #4 remake .. " + repr(E))
            return -1

    """
    C. Public Functions
    """
    # [C.1] write some actions to hardware
    def write(self, image = None, text =None,
                    led = None,
                    servo_angle = None, servo_time = None,
                    serial_msg = None):

        try :
            # 1. send image
            if image is not None:
                result = self.OLED.send_image(image)
                if result == -1 and self.log is not None :  # if error occur, reset object
                    self.log.error(self.OLED.last_exception)
                    self.OLED.last_exception = ""

            # 2. send text
            if text is not None:
                result = self.OLED.send_text(text)
                if result == -1 and self.log is not None :  # if error occur, reset object
                    self.log.error(self.OLED.last_exception)
                    self.OLED.last_exception = ""

            # 3. send led
            if led is not None:
                result = self.RGB_LED.write(led)
                if result == -1 and self.log is not None :  # if error occur, reset object
                    self.log.error(self.RGB_LED.last_exception)
                    self.RGB_LED.last_exception = ""

            # 4. send servo
            if servo_angle is not None:
                result = self.SERVO.write(servo_angle,servo_time)
                if result == -1 and self.log is not None :  # if error occur, reset object
                    self.log.error(self.SERVO.last_exception)
                    self.SERVO.last_exception = ""

            # 5. send serial msg
            if serial_msg is not None:
                result = self.UART.write(serial_msg)
                if result == -1 and self.log is not None:  # if error occur, reset object
                    self.log.error(self.UART.last_exception)
                    self.UART.last_exception = ""

            # 6. check Error Logs
            if self.log is not None :  # if error occur, reset object
                for comp in [self.OLED,self.RGB_LED,self.SERVO, self.SENSOR]:
                    if len(comp.last_exception) :
                        self.log.error(comp.last_exception)
                        comp.last_exception = ""

        except Exception as E:  # if error occur, reset all object
            self.log.warning("HardwareV1.write(), "+repr(E))
            self.reset()
            return -1

        else:
            return 0

    # [C.2] read data from hardware
    def read(self,sw_reset = False):
        volume = self.SENSOR.volume
        distance = self.SENSOR.distance
        serial_msgs = self.UART.received_msg

        if sw_reset is True:
            self.SENSOR.sw_flag = False
        return volume, distance, serial_msgs

    """
    D. Private Functions
    """
    # [D.1] set hardware as default value
    # TODO : SET REAL VALUE.
    def __set_default(self):
        self.OLED.send_console(3,"Hardware init...   \n"+
                                 "Hardware reset..   \n"+
                                 "Hardware Done!..   ")
        self.RGB_LED.write([100,50,50,50,100,50])
        self.SERVO.write([0,0,0,0,0],1)

    # [D.2] load logger
    @staticmethod
    def __set_logger():
        # 2.1 set logger and formatter
        log = logging.getLogger("Hardware_V1")
        log.setLevel(logging.DEBUG)
        formatter = logging.Formatter('[%(levelname)s] (%(asctime)s : %(filename)s:%(lineno)d) > %(message)s')

        # 2.2 set file logger
        log_file = logging.FileHandler(filename = '/home/pi/Desktop/PinoBot/log/HardwareV11.log',
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

"""
Module TEST codes 
"""
def test():
    hardware = HardwareV1("")

    # valid case
    hardware.write(text="하이루",led=[0,0,100],servo_angle=[180,180,90],servo_time=2)
    hardware.write(image="test.jpg")
    hardware.write(text="아아")
    hardware.write(serial_msg="test_msg_logs")

    # invalid case
    hardware.write(text = 1)
    hardware.write(led  = 1)
    hardware.write(servo_angle = 1)
    hardware.write(serial_msg= 1)

if __name__ == '__main__':
    test()
