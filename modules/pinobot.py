#!/usr/bin/python3


from modules.pino_boot_loader import PinoBootLoader
import time , threading, logging
from logging.handlers import RotatingFileHandler
from enum import Enum
from google.api_core.exceptions import Unknown


class PinoState(Enum):
    IDLE = 0
    SENSOR_ON =1
    STILL_ON = 2
    SENSOR_OFF = 3
    LISTEN_SUCCESS = 11
    LISTEN_FAIL = 12
    LISTEN_CLOUD_ERROR = 13
    UART_ON = 20
    DO_SOMETHING = 30
    #GO_SLEEP = 4
    #WAKEP_UP = 5

class PinoBot:
    """
    Description:
        pinobot main module
    -

    Summary of Class

        1. setup(self):
            set logging and boot pinobot

        2. update(self):
            read hardware and update PinoBot's State

        3. listen(self):
            start audio recording and streaming and return response
            if google cloud error occurs, display to OLED

        4. say(self,response):
            pinobot say tts response

        5. act(self, response):
            pinobot do action by response.action_cmd

        6. call_uart_event(self):
            if pinobot's uart got some message,
            use this to call dialogflow event

        5. call_intent(self,text = "" ,event_name="", event_parameter=None):
            call dialogflow manually by dict or text, and get responses
    """
    def __init__(self):
        # 0. Argument
        # 1. Static Variables

        # 2. variables
        self.cur_volume = 0  # current speaker volume rate [ 0 ~ 10 ]
        self.detect = {
            "pre_state": 0,  # last sensor state, 1: in , 0: out
            "distance": 30,  # cm                 # sonic sensor threshold to between 1 to 0
            "first_time": time.time(),
        }  # sec   # first time sonic sensor detect object
        self.base_path = "/home/pi/Desktop/Arduino_Dialogflow/"
        self.state = PinoState.IDLE

        # 3. Objects
        self.hardware = None
        self.cloud = None
        self.config = None
        self.log = None
        self.response = None
        self.uart_cmd = None

        # threads
        self.say_thread = None
        self.act_thread = None

        # 4. Run setup
        self.setup()

    def setup(self):
        """
        Description
        -----------
            set logging and boot pinobot

        """
        # 1. init log
        path = self.base_path + "/main.log"
        self.log = logging.getLogger("Main")
        self.log.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "[%(levelname)s] (%(asctime)s : %(filename)s:%(lineno)d) > %(message)s"
        )
        log_file = RotatingFileHandler(
            filename=path, maxBytes=5 * 1024 * 1024, mode="w", encoding="utf-8"
        )
        log_file.setFormatter(formatter)
        self.log.addHandler(log_file)
        log_console = logging.StreamHandler()
        log_console.setFormatter(formatter)
        self.log.addHandler(log_console)
        self.log.info("[PinoBot] Start Boot")
        boot = PinoBootLoader(self.base_path,self.log)

        # 2. run boot sequence
        self.hardware, self.cloud, self.config = boot.boot()
        del boot

        self.log.info("[PinoBot] Boot Done..")

    def update(self):
        """ 
        Description
        -----------        
            read hardware and update PinoBot's State

        Notes
        -----
            State : PinoState
            priority [1] : Serial command
            priority [2] : ultrasonic sensor state

            If the ultrasonic sensor and uart command come in at the same time,
            the uart command is given priority.

        """

        # 2. read hardware signals
        cur_sensor_state = 0
        distance,uart_cmd = self.hardware.read()
        if self.detect["distance"] > distance > 4:
            cur_sensor_state = 1

        # 3. uart command on
        if uart_cmd is not None:
            self.uart_cmd = uart_cmd
            self.state = PinoState.UART_ON
            print("uart : ",self.uart_cmd)
            return self.state

        # 4. set state by sensor
        if self.detect["pre_state"] == 0 and cur_sensor_state == 1:
            # 4.1 object [ 0 -> 1 ] , new object, add talk task
            self.detect["first_time"] = time.time()
            self.state = PinoState.SENSOR_ON

        elif self.detect["pre_state"] == 1 and cur_sensor_state == 1:
            # 4.2 object [ 1 -> 1 ] , object still in
            self.state = PinoState.STILL_ON

        elif self.detect["pre_state"] == 1 and cur_sensor_state == 0:
            # 4.3 object [ 1 -> 0 ] , object gone
            self.state = PinoState.SENSOR_OFF

        self.detect["pre_state"] = cur_sensor_state  # update sensor state
        return self.state

    def listen(self):
        """
        Description
        -----------
            start audio recording and streaming and return response
            if google cloud error occurs, display to OLED

        Return
        ------
            response : { Parsed DialogFlow response  , PinoResponse object}

        """

        self.log.info("listen")
        self.hardware.write(text="듣는중")
        # 2.1. streaming voice
        if self.cloud.start_stream() == -1:
            self.hardware.write(text="녹음 실패\n ㅠㅠ")
            return None

        self.hardware.write(text="듣는중..")
        try:
            response = self.cloud.get_stream_response()
            if response.stt_result == "[Fail]":
                self.state = PinoState.LISTEN_FAIL
                return None

            # 2.E0. Gcloud Error
            if self.cloud.gcloud_state < 0:
                self.state = PinoState.LISTEN_CLOUD_ERROR
                if self.cloud.gcloud_state == -1:  # Internet Error
                    self.hardware.write(text="인터넷 문제\n 가 있어요 ㅠㅠ ")
                elif self.cloud.gcloud_state == -2:  # google server error
                    self.hardware.write(text="인터넷 문제\n 가 있어요 ㅠㅠ ")
                elif self.cloud.gcloud_state == -3:
                    self.hardware.write(text="오늘의 할당량을 \n 다 사용했네요 ㅠㅠ")
                elif self.cloud.gcloud_state < -3:
                    self.hardware.write(text="무언가 문제가 있어요 \n ㅠㅠ")
                self.log.warning("[PinoBot] cloud Error type : %d" % self.cloud.gcloud_state)


        except Exception as E:
            self.log.error("[PinoBot] listen Error : %s" % repr(E))
            return None
        else:
            return response


    def start_say(self, response):
        """
        Description
        -----------
            pinobot say tts response

        Parameters
        ----------
            response : { Parsed DialogFlow response  , PinoResponse object}
                PinoResponse.tts_result is audio binary file .wav format

        [TODO] add local wave file play feature
        """

        if response is None:
            self.log.warning("say.. nothing")
            return 0

        try:
            self.say_thread = threading.Thread(
                target=self.cloud.play_audio_response, args=(response,)
            )
            self.say_thread.start()
        except Exception as E:
            self.log.error("[PinoBot] say Error : %s" % repr(E))
            return -1

    def start_act(self, response):
        """
        Description
        -----------
            pinobot do action by response.action_cmd

        Notes
        -----
            action could take few seconds, therefor add threading

        Parameters
        ----------
            response : { Parsed DialogFlow response  , PinoResponse object}
                PinoResponse.action_cmd is list of comaands

        Return
        ------
            result :    0 Success
                        1 Fail

        """

        if response is None:
            self.log.warning('act.. nothing')
            return 0

        try:
            self.act_thread = threading.Thread(
                target=self.hardware.run_pinobot_cmd, args=(response,)
            )
            self.act_thread.start()
        except Exception as E:
            self.log.error("[PinoBot] act Error : %s" % repr(E))
            return -1
        else :
            return 0

    def wait_say_and_act(self,timeout = 30):
        """
        Description
        -----------
            wait until say and act finish

        Parameters
        ----------
            timeout : seconds {int or float}

        Return
        ------
            result :    0 Success
                        1 Fail

        """
        self.state = PinoState.DO_SOMETHING
        if self.act_thread  and self.say_thread :
            for i in range (int(timeout*1000)):
                if self.act_thread.is_alive() and self.say_thread.is_alive():
                    time.sleep(0.01)
                else :
                    return 0

        # [TODO] add flag to all thread and make ways to force stop.
        return -1



    def call_uart_event(self):
        """
        Description
        -----------
            if pinobot's uart got some message,
            use this to call dialogflow event

        Notes
        -----
            uart_cmd : { dict }
            {   event_name : $name ,
                para1Name  : $para1Value,
                ...
                paraNName  : $paraNValue,
            }

        Return
        ------
            response : { Parsed DialogFlow response  , PinoResponse object}
z
        """
        try:
            if self.uart_cmd is not None:
                self.hardware.write(text="메세지 확인중..")
                response = self.cloud.send_event(self.uart_cmd ['event_name'], self.uart_cmd )
                self.uart_cmd = None  # reset
                self.state = PinoState.IDLE
                self.hardware.write(serial_msg = "ready")
                return response
            else:
                self.hardware.write(serial_msg = "ready")
                return self.cloud.parsing_response(None,None,None)

        except Exception as E:
            self.log.error("[PinoBot] call_uart_event Error : %s" % repr(E))
            return None

    def call_intent(self,text = "" ,event_name="", event_parameter=None):
        """
        Description
        -----------
            call dialogflow manually by dict or text, and get responses

        Parameters
        ----------
            text : natural word message to call dialogflow  {  str, optional }
            event_name : dialogflow intent event name       {  str, optional }
            event_parameter : dialogflow intent parameter   { dict, optional }
                 event_parameter without event_name is useless

        Return
        ------
            response : { Parsed DialogFlow response  , PinoResponse object}

        Example
        -------
            r = bot.call_intent(text = '안녕하세요')
            print(r.intent_response)
            >> 반갑습니다 저는 피노봇입니다

            r = bot.call_intent("weather",{'humidity:'50','temp':'20'}
            print(r.intent_response)
            >> 지금 방의 상태를 알려드립니다, 습도는 50프로 온도는 20도입니다.

        """
        try :
            if event_name is not "":
                self.cloud.send_event(event_name, event_parameter)
                return self.cloud.parsing_response()
        except Exception as E:
            self.log.error("[PinoBot] call_intent Error : %s" % repr(E))
            return None

    def return_idle(self):
        """
        Description
        -----------
            display idle message and
            return state to idle

        """
        self.hardware.write(text="대기중..")
        self.state = PinoState.IDLE
