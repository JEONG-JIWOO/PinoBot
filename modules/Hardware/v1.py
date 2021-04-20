#!/usr/bin/python3
"""
Description : PinoBot V1 Hardware Control Module
Author : Jiwoo Jeong
Email  : Jiwoo@gepetto.io  / jjw951215@gmail.com
Reference:
    pip3 install adafruit-circuitpython-ssd1306
    https://github.com/adafruit/Adafruit_CircuitPython_SSD1306


V 0.9  [2021-02-13]
    - still using old version
    - add comment form

v 1.0 [ WIP ]
    - [X, refactoring   ] remove hard codded code
    - [X, enhancement   ] remove reset function
    - [X, enhancement   ] remove to many try and except
    - [X, enhancement   ] log module come from pinobot
    - [X, documentation ] add Comment
    - [X, development   ] add run_pinobot_cmd function

"""
from modules.Hardware import pino_sensor, pino_uart
from modules.Hardware.I2C import pino_servo, pino_oled
from modules.Hardware.SPI import pino_led

import ast ,time, numbers
import board


class Hardware:
    """
    Description:
        pinobot hardware control module
    -

    Summary of Class

        1. write( serial_msg=None, image=None, text=None, led=None, servo_angle=None ,servo_time=0.2)):
            control hardware

        2. read(self):
            read sensors and communication  and return value

        3. set_default(self):
            set all hardware as default value.

        4. display_console(self, step, msgs, mode="a"):
            wrapper of pino_oled.py send_loading_console()

        5. run_pinobot_cmd(self, pino_response):
            run pinobot actuating command in  "pino_response.action_cmd"
            could take few seconds [ blocking function ]
            therefor threading is recommended

    """
    def __init__(self, config, base_path,log):
        self.config = config
        self.base_path = base_path
        self.log = log
        self.state = {'I2C'     :False,
                      'OLED'    :False,
                      'SERVO'   :False,
                      'RGB_LED' :False,
                      'SENSOR'  :False,
                      'UART'    :False
                      }
        self.I2C_BUS = None
        self.OLED = None
        self.SERVO = None
        self.RGB_LED = None
        self.SENSOR = None
        self.UART = None
        self.reset()

    def reset(self):
        try:
            self.I2C_BUS = board.I2C()
        except Exception as E:
            self.log.error("pino_hardware.py: i2c error"+repr(E))
        else :
            self.state['I2C'] = True


        try :
            self.OLED = pino_oled.Pino_OLED(
                self.I2C_BUS,
                self.base_path,
                console_font_name=self.config["OLED"]["console_font"],
                main_font_name=self.config["OLED"]["main_font"],
            )
        except Exception as E:
            self.log.error("pino_hardware.py: OLED error"+repr(E))
        else :
            self.state['OLED'] = True


        try :
            self.SERVO = pino_servo.Pino_SERVO(
                self.I2C_BUS,
                num_motor=int(self.config["MOTOR"]["num_motor"]),
                motor_enable=ast.literal_eval(self.config["MOTOR"]["motor_enable"]),
                motor_min_angle=ast.literal_eval(
                    self.config["MOTOR"]["motor_min_angle"]
                ),
                motor_max_angle=ast.literal_eval(
                    self.config["MOTOR"]["motor_max_angle"]
                ),
                motor_default_angle=ast.literal_eval(
                    self.config["MOTOR"]["motor_default_angle"]
                ),
            )
        except Exception as E:
            self.log.error("pino_hardware.py: SERVO error "+repr(E))
        else :
            self.state['SERVO'] = True


        try :
            self.RGB_LED = pino_led.Pino_LED(
                on=ast.literal_eval(self.config["LED"]["ON"])
            )  # rec error occur
        except Exception as E:
            self.log.error("pino_hardware.py: SPI RGB LED error "+repr(E))
        else :
            self.state['RGB_LED'] = True


        try :
            self.SENSOR = pino_sensor.Pino_GPIO()
        except Exception as E:
            self.log.error("pino_hardware.py: GPIO error "+repr(E))
        else :
            self.state['SENSOR'] = True


        try :
            self.UART = pino_uart.Pino_UART(
                baud_rate=int(self.config["UART"]["baud_rate"])
            )
        except Exception as E:
            self.log.error("pino_hardware.py: UART error"+repr(E))
        else :
            self.state['UART'] = True

        self.log.info("hardware state : "+str(self.state))
        #print("hardware state : "+str(self.state))
        self.set_default()

    """
    A. Public Functions
    """
    # [C.1] write some actions to hardware
    def write(
        self,
        serial_msg=None,
        image=None,
        text=None,
        led=None,
        servo_angle=None,
        servo_time=0.2,
    ):
        """
        Description
        -----------
            control hardware

        Parameters
        ----------
            serial_msg          : text to wrtie on uart          { str   } ,optional
            image               : image file to show on lcd path { str   } ,optional
            text                : text to show on lcd            { str   } ,optional
            led                 : led colors in rgb              { list  } ,optional
                length : 3 or 6
                value  : 0 ~ 255
                ex) [255,255,255] -> RGB(255,255,255) : white color  on two led
                ex) [255,0,0,255,255,255] -> RGB(255,255,255) : red color and  white color

            servo_angle         : servo motor target angles      { list  } ,optional
                length : 1 ~ 8
                value  : 0 ~ 180
                ex) [10,20,30] : #1 servo-> 10 degree,  #2 servo-> 20 degree,  #3 servo-> 30 degree,
                if servo_time is not defined, set to 0.2 as default

            servo_time     : servo motor actuate time       { float } ,optional
                range  : 0 ~ 10

        Example
        -------
            h = hardware(config, base_path)
            h.write(serial_msg = "ready!")
            h.write(image = "1.png")
            h.write(text  = "I'm ready!")
            h.write(led  = [255,255,255])
            h.write(servo_angle = [0,10,20,30,40] , servo_time 0.4

        """

        # 1. send image
        if self.state['OLED'] and image is not None and isinstance(image, str):
            try :
                self.OLED.send_image(image)
            except Exception as E :
                self.log.warning("pino_oled.py: " + repr(E))
                return -1

        # 2. send text
        if self.state['OLED'] and text is not None and isinstance(text, str):
            try:
                self.OLED.send_text(text)
            except Exception as E:
                self.log.warning("pino_oled.py: " + repr(E))
                return -1

        # 3. send led
        if self.state['RGB_LED'] and  led is not None and isinstance(led, list):
            try:
                self.RGB_LED.write(led)
            except Exception as E:
                self.log.warning("pino_led.py: " + repr(E))
                return -1

        # 4. send servo
        if self.state['SERVO'] and  servo_angle is not None and isinstance(servo_angle, list):
            try:
                self.SERVO.write(servo_angle, servo_time)
            except Exception as E:
                self.log.warning("pino_servo.py: " + repr(E))
                return -1

        if self.state['UART'] and serial_msg is not None and isinstance(serial_msg, str):
            try:
                self.UART.write(serial_msg)
            except Exception as E:
                self.log.warning("pino_uart.py: " + repr(E))
                return -1

        return 0


    # [C.2] read data from hardware
    def read(self):
        """
        Description
        -----------
            read sensors and communication  and return value

        Return
        ------
            distance    : ultrasonic sensor value , { float , cm }
            uart_data   : {dict}
                {   event_name : $name ,
                    para1Name  : $para1Value,
                    para2Name  : $para2Value,
                    para3Name  : $para3Value,
                    ...
                    paraNName  : $paraNValue,
                }

        Example
        -------
            h = hardware(config, base_path)
            sensor_distance , serial_msg = h.read()
            print("distance is %2.2f cm"%sensor_distance)
            print("arduino has event : %s "%serial_msg['event_name'])

        """
        distance = -1
        if  self.state['SENSOR'] :
            self.SENSOR.read_sonic_sensor()
            distance = self.SENSOR.distance
        # volume = self.SENSOR.volume    ->  volume not used for now
        # self.SENSOR.sw_flag = False
        uart_data = None
        if self.state['UART']:
            uart_data =self.UART.read()

        return distance, uart_data

    def set_default(self):
        """
        Description
        -----------
            set all hardware as default value.

        """

        if self.state['RGB_LED']:
            self.RGB_LED.write([20, 20, 20, 20, 20, 20])
        if self.state['SERVO']:
            self.SERVO.set_default()

    def display_console(self, step, msgs, mode="a"):
        """
        Description
        -----------
            wrapper of pino_oled.py send_loading_console()

        """
        if self.state['OLED']:
            self.OLED.send_loading_console(step, msgs, mode=mode)

    def run_pinobot_cmd(self, pino_response):
        """
        Description
        -----------
            run pinobot actuating command in  "pino_response.action_cmd"
            could take few seconds [ blocking function ]
            therefor threading is recommended

        Parameters
        ----------
        pino_response { pino_dialogflow.py | PinoResponse }:
            pino_response.stt_result             :  stt text (str)
            pino_response.tts_result             :  audio .wav format (binary file)
            pino_response.intent_name            :  intent name (str)
            pino_response.intent_response        :  intent response text (str)
            pino_response.intent_parameter = {}  :  intent parameter (dict)
            pino_response.action_cmd = []        :  pinobot command (list)

        Notes
        -----
        to handler lower, and upper case error in command,
        use .lower() to all command str and compare it

        pino_response.action_cmd: [
                [cmd1_name, cmd1_value],
                [cmd2_name, cmd2_value],
                [cmd3_name, cmd3_value],
                ...
                [cmdn_name, cmdn_value],
            ]

        cmd_name :
            ordered command :
                n_PinoMotor
                n_Pinowait ...

            if un_ordered command, like
                pinoSerialMSg,
                -> set to last
                _> act randomly after all ordered cmd done,


        Example
        -------

        """
        # 1. line up commands

        ordered_cmds = []
        for cn , cmd_value in pino_response.action_cmd:
            cmd_b = cn.split("_")
            # 1.1 "_" not in cmd_name : un_ordered command
            if len(cmd_b) == 1:
                ordered_cmds.append([1000,cn,cmd_value])

            # 1.2 ordered command
            elif len(cmd_b) > 1 :
                cmd_name_pure = "_".join(cmd_b[1:])
                try :
                    order = ast.literal_eval(cmd_b[0])

                # 1.2.1 fail to parse order
                except ValueError :
                    error_msg = pino_response.intent_name +"\n" + cmd_name_pure+"\n name error"
                    self.write(text=error_msg)
                    self.log.info("wrong cmd"+ pino_response.intent_name +" | " + cmd_name_pure)
                    ordered_cmds.append([1000, cmd_name_pure,cmd_value])

                # 1.2.2 success to parse order
                else :
                    ordered_cmds.append([order, cmd_name_pure, cmd_value])

        ordered_cmds = sorted(ordered_cmds, key=lambda x: x[0])
        #print(ordered_cmds)

        # 2. run ordered command
        for order,cmd_name,cmd_value in ordered_cmds:

            cmd_name_lc = cmd_name.lower()
            if cmd_name_lc  == "PinoMotor".lower():
                try:
                    args = ast.literal_eval(cmd_value)
                    if not isinstance(args,list):
                        raise ValueError
                    servo_time = float(args[0])
                except ValueError:
                    self.log.warning("pino_hardware.py: cmd_value_error " + pino_response.intent_name+" | "+ cmd_name)
                    self.write(text="%s \n parameter error\n %s"%(pino_response.intent_name[:16],cmd_name))
                else :
                    self.write(servo_angle=args[1:], servo_time=servo_time)

            elif cmd_name_lc == "PinoWait".lower():
                try:
                    args = ast.literal_eval(cmd_value)
                    if not isinstance(args,numbers.Number):
                        raise ValueError
                except ValueError:
                    self.log.warning("pino_hardware.py: cmd_value_error " + pino_response.intent_name +" | "+ cmd_name)
                    self.write(text="%s \n parameter error\n %s"%(pino_response.intent_name[:16],cmd_name))
                else:
                    time.sleep(args)

            elif cmd_name_lc == "PinoLED".lower():
                try:
                    args = ast.literal_eval(cmd_value)
                    if not isinstance(args, list):
                        raise ValueError
                except ValueError:
                    self.log.warning("pino_hardware.py: cmd_value_error " + pino_response.intent_name +" | "+ cmd_name)
                    self.write(text="%s \n parameter error\n %s"%(pino_response.intent_name[:16],cmd_name))
                else:
                    self.write(led=args)

            elif cmd_name_lc == "PinoSerialMsg".lower():
                self.write(serial_msg=cmd_value)

            elif cmd_name_lc == "PinoShowText".lower():
                self.write(text=cmd_value)

            elif cmd_name_lc == "PinoShowImage".lower():
                self.write(image=cmd_value)

            elif cmd_name_lc == "PinoExpress".lower():
                # TODO : actuate prebuild face emotion
                pass

    def ramdon_motion(self,t):
        rm = self.SERVO.cal_random_motion(t)
        self.SERVO.write(rm[1:], t)