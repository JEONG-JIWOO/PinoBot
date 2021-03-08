#!/usr/bin/python3

"""
Description : PinoBot Rpi Uart(serial0) handling module
Author : Jiwoo Jeong
Email  : Jiwoo@gepetto.io  / jjw951215@gmail.com

V 1.0
    - make module and test done

V 1.0.1 [2021-02-16]
    - [O, refactoring   ] remove hard codded code
    - [O, enhancement   ] remove reset function
    - [O, enhancement   ] remove to many try and except
    - [O, documentation ] add Comment

"""

import serial
import ast , time


class Pino_UART:
    """
    Description:
    - Uart Module for use in pinobot

    Summary of Class

        1. write(self, str_msg="", pino_response = None):

        2. read(self):

    """

    def __init__(self, port="/dev/serial0", baud_rate=115200):
        # 0. Argument
        self.port = port       # Rpi basic : /dev/serial0
        self.baud = baud_rate  # default   : 115200

        self.last_exception = ""  # save exception message for logging
        self.parsed_data = {}

        # 3. Objects
        self.pino_serial = serial.Serial(
                self.port, self.baud, timeout=0, write_timeout=0.05
            )


    # [B.1] write "string" or "DialogFlow result" to serial port
    def write(self, str_msg="", pino_response = None):
        """
        Description
        -----------
            send string message or pino_response

        Parameters
        ----------
            str_msg: message to send {str, optional}

            pino_response { pino_dialogflow.py | PinoResponse , optional}:
                pino_response.stt_result             :  stt text (str)
                pino_response.tts_result             :  audio .wav format (binary file)
                pino_response.intent_name            :  intent name (str)
                pino_response.intent_response        :  intent response text (str)
                pino_response.intent_parameter = {}  :  intent parameter (dict)
                pino_response.action_cmd = []        :  pinobot command (list)

        Notes
        -----
            [Serial protocol send Rpi to Arduino]

                $stt|$intent_name|$intent_response|$num_action_parameter|$action_parameter_1_key:$action_parameter_2_value..

                ex1 파라미터 0개일때:
                    안녕하세요|Welcome|반가워요|0
                        stt결과 : 안녕하세요
                        DialogFlow 인텐트 이름  : Welcome
                        DialogFlow 응답 텍스트  : 반가워요
                        DialogFlow 파라미터 개수 : 0


                ex2 파라미터 1개일때:
                    안녕하세요|Welcome|반가워요|1|play_sound:1.wav|
                        DialogFlow 파라미터 개수 : 1
                        파라미터1 이름 : play_sound
                        파라미터1 값   : 1.wav


                ex2 파라미터 2개일때:
                    안녕하세요|Welcome|반가워요|2|play_sound:1.wav|temp:30
                        DialogFlow 파라미터 개수 : 2
                        파라미터1 이름 : play_sound
                        파라미터2 값   : 1.wav
                        파라미터2 이름 : temp
                        파라미터2 값   : 30

        Return
        ------
            result : fail   -1
                     success 0

        Example
        -------
            uart = Pino_UART()
            uart.write("ready")

            Gbot.start_stream()
            result2 = Gbot.get_stream_response()
            uart.write(pino_response=result2)

        """

        try:
            # 1.1 send DialogFlow result
            if pino_response is not None :
                new_msg = "%s|%s|%s|%d"%(pino_response.stt_result,
                                         pino_response.intent_name,
                                         pino_response.intent_response,
                                         len(pino_response.intent_parameter))

                action_dict = pino_response.intent_parameter
                for action_parameter in action_dict.keys():
                    new_msg += "|%s:%s"%(action_parameter, action_dict[action_parameter])
                self.pino_serial.write(new_msg.encode())

            # 1.2 or send just string message
            elif str_msg != "":
                self.pino_serial.write(str_msg.encode())

        # 2. if Fail to send data
        except Exception as E:
            self.last_exception = "PINO_UART.write()" + repr(E)  # save Error message to class for log
            return -1
        # 3. Success to send data
        else:
            return 0

    # [B.2] read msgs form serial port , if exist.
    def read(self):
        """
        Description
        -----------
            read serial port without block
            and parse and return

        Notes
        -----
            [Serial protocol receive form  Arduino]
            event_name:$name|para1Name:$para1Value|para2Name:$para2Value|para3Name:$para3Value|para4Name:$para1Value

            after decode
            {   event_name : $name ,
                para1Name  : $para1Value,
                para2Name  : $para2Value,
                para3Name  : $para3Value,
                ...
                paraNName  : $paraNValue,
            }

            ex)
                event_name:humidity_event|humidity:50|temp:12.3|cds:457


        Return
        ------
            parsed_data : {dict}
                ex)
                    {
                        event_name : humidity_event,
                        humidity   : 50,
                        temp       : 12.3,
                        cds        : 457
                    }

        """
        # 1. read serial data
        received_msg = ""
        try:
            data_left = self.pino_serial.inWaiting()
            time.sleep(0.01)            # wait for get all data
            if  data_left > 0:
                time.sleep(0.2)
                data_left = self.pino_serial.inWaiting()
                received_msg = str(self.pino_serial.read(data_left).decode())
                self.pino_serial.flushInput()
            else :
                return None
        except Exception as E:
            self.last_exception = "PINO_UART.read()" + repr(E) # save Error message to class for log
            return None

        # 2. if there are empty message , clear buffer and return None
        if received_msg is "":
            self.pino_serial.flushInput()
            return None
        blocks = received_msg.split("|")

        # 3. split each word
        parsed_data = {}
        for block in blocks:
            b2 = block.split(":")
            if len(b2) == 2:
                parameter_name = b2[0]
                parsed_data[parameter_name] = b2[1]

        # 4. try to convert string to float or int
        for k in parsed_data.keys():
            try:
                new_value = ast.literal_eval(parsed_data[k])
            except ValueError :
                pass
            else :
                parsed_data.update({k:new_value})

        # 5. check parse response in valid and return
        if 'event_name' not in parsed_data or len(parsed_data) < 1 :
            return None
        else :
            self.parsed_data = parsed_data
            return parsed_data
