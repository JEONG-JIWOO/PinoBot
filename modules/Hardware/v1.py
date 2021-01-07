#!/usr/bin/python3
"""
Write By Jiwoo Jeong

PinoBot V1 Hardware Control Module

"""
import logging , time
import board

from modules.Hardware.I2C import pino_servo , pino_oled
from modules.Hardware import pino_sensor , pino_uart
from modules.Hardware.SPI import pino_led

class HardwareV1:
    """
    A. con & deconstruct
    """
    def __init__(self,config,base_path):
        # 0. Argument
        self.config = config
        self.base_path = base_path

        # 1. Static Variables

        # 2. variables
        self.last_reset_time = 0
        self.last_exception = ""
        self.version = "0.9.2"

        # 3. Objects
        self.I2C_BUS = None
        #self.SPI_BUS = None  for now, net used due to conflict with seeed-voicecard

        self.UART = None
        self.SERVO = None
        self.OLED = None
        self.RGB_LED = None
        self.SENSOR = None

        self.log = None

        # 4. Init Functions
        self.reset()
        #self.__set_default()

    def __del__(self):
        for sub_modules in [self.SERVO, self.OLED , self.RGB_LED , self.SENSOR]:
            if sub_modules is not None:
                try:
                    del sub_modules
                except Exception as E:
                    self.log.warning("HardwareV1.del()," + repr(E))
        self.I2C_BUS.deinit()
        del self.I2C_BUS

    """
    B. reset 
    """
    def reset(self):
        # 1. check last reset time,
        #    only can reset after 1min after last reset
        if (time.time() - self.last_reset_time) < 60:
            return 0

        # 2. if object exists..
        for sub_modules in [self.SERVO, self.OLED , self.RGB_LED , self.SENSOR, self.I2C_BUS]:
            if sub_modules is not None:
                try:
                    del sub_modules
                except Exception as E:
                    self.log.warning("HardwareV1.reset(), #2. del " + repr(E))

        # 3. refresh last reset time
        self.last_reset_time = time.time()

        # 4. re open GPIO
        try:
            # 4.1 init log
            self.log = self.__set_logger()

            # 4.2 init bus
            import ast
            self.I2C_BUS = board.I2C()

            # 4.3 init SubModules
            self.OLED = pino_oled.Pino_OLED(self.I2C_BUS, self.base_path,
                                            console_font_name=self.config['OLED']["console_font"],
                                            main_font_name=self.config['OLED']["main_font"])
            self.SERVO = pino_servo.Pino_SERVO(self.I2C_BUS,
                                               num_motor=int(self.config['MOTOR']['num_motor']),
                                               motor_enable=ast.literal_eval(self.config['MOTOR']['motor_enable']),
                                               motor_min_angle=ast.literal_eval(
                                                   self.config['MOTOR']['motor_min_angle']),
                                               motor_max_angle=ast.literal_eval(
                                                   self.config['MOTOR']['motor_max_angle']),
                                               motor_default_angle=ast.literal_eval(
                                                   self.config['MOTOR']['motor_default_angle'])
                                               )
            self.RGB_LED = pino_led.Pino_LED(on=ast.literal_eval(self.config['LED']['ON'])) # rec error occur
            self.SENSOR = pino_sensor.Pino_GPIO()
            self.UART = pino_uart.Pino_UART(baud_rate=int(self.config['UART']['baud_rate']))

        except Exception as E:
            self.log.warning("HardwareV1.reset() , #4 remake .. " + repr(E))
            return -1

    """
    C. Public Functions
    """
    # [C.1] write some actions to hardware
    def write(self, image = None, text =None,
                    led = None,
                    servo_angle = None, servo_time = 0.2,
                    serial_msg = None):


        # 1. send image
        if image is not None and isinstance(image, str):
            result = self.OLED.send_image(image)
            if result == -2 and self.log is not None :  # image file not Found.
                self.log.warning(self.OLED.last_exception)

            elif result == -1 and self.log is not None :  # Critical Error
                self.log.error(self.OLED.last_exception)  # Write Error Message
                self.OLED.reset()  # reset OLED

        # 2. send text
        if text is not None and isinstance(text, str):
            result = self.OLED.send_text(text)
            if result == -1 and self.log is not None :  # if error occur
                self.log.error(self.OLED.last_exception)  # Write Error Message
                self.OLED.reset()  # reset OLED

        # 3. send led
        if led is not None and isinstance(led, list):
            result = self.RGB_LED.write(led)
            if result == -1 and self.log is not None :  # if error occur
                self.log.error(self.RGB_LED.last_exception)
                self.RGB_LED.reset()  # reset OLED

        # 4. send servo
        if servo_angle is not None and isinstance(servo_angle, list):
            """
            NOTE:
            SERVO,write is block functions during "servo_time"
            if you want to force stop, set self.SERVO.force_stop_flag = True
            """
            result = self.SERVO.write(servo_angle,servo_time)
            if result == -1 and self.log is not None :  # if error occur
                self.log.error(self.SERVO.last_exception)
                self.SERVO.reset()

        # 5. send serial msg
        if serial_msg is not None and isinstance(serial_msg, str):
            result = self.UART.write(serial_msg)
            if result == -1 and self.log is not None:  # if error occur, reset object
                self.log.error(self.UART.last_exception)
                self.UART.reset()

        # 6. check sub_module Error Logs
        if self.log is not None :  # if error occur, reset object
            for sub_module in [self.OLED,self.RGB_LED,self.SERVO, self.SENSOR]:
                if len(sub_module.last_exception) :
                    self.log.error(sub_module.last_exception)
                    sub_module.last_exception = ""


    # [C.2] read data from hardware
    def read(self):
        self.SENSOR.read_sonic_sensor()
        #print("v1 %f"%self.SENSOR.distance)
        volume = self.SENSOR.volume
        distance = self.SENSOR.distance
        serial_msgs = self.UART.received_msg
        self.SENSOR.sw_flag = False

        if self.UART.received_msg != "":
            self.UART.received_msg = ""

        return volume, distance, serial_msgs


    """
    D. Private Functions
    """
    # [D.1] set hardware as default value
    # TODO : SET REAL VALUE.
    def __set_default(self):
        #self.OLED.send_console(1,"Hardware Done!..   \n")
        self.RGB_LED.write([20,20,20,20,20,20])
        self.SERVO.write([45,45,90,0,0],1)

    # [D.2] load logger
    def __set_logger(self):
        # 2.1 set logger and formatter
        log = logging.getLogger("Hardware_V1")
        log.setLevel(logging.DEBUG)
        formatter = logging.Formatter('[%(levelname)s] (%(asctime)s : %(filename)s:%(lineno)d) > %(message)s')

        # 2.2 set file logger
        log_file = logging.FileHandler(filename = self.base_path+'log/HardwareV1.log',
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

