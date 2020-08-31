#!/usr/bin/env python3.7

import time, random , queue

from Core.pino_init import Pino_Init
from Core.pino_custom_cmd import run_pino_custom_cmd
import ast , datetime

from google.protobuf.json_format import MessageToDict
import threading
import logging
from logging.handlers import RotatingFileHandler


class PinoBot:
    def __init__(self):
        # 0. Argument
        # 1. Static Variables

        # 2. variables
        self.cur_volume = 0                               # current speaker volume rate [ 0 ~ 10 ]

        self.sleep = {"state":False,                      # "Sleep_Mode" state, True or False
                      "enter_limit_time":60, # sec        # how much time sensor detect object, change to "Sleep_Mode"
                      "task_probability":0.01,            # "Sleep_Mode_Task" in this random probability
                      "task_min_time" : 30,  # sec        # minimum "Sleep_Mode_Task" duration
                      "task_last_time":time.time() }# sec # last time when "Sleep_Mode_Task" occur

        self.detect ={"pre_state":0,                      # last sensor state, 1: in , 0: out
                      "distance":30, # cm                 # sonic sensor threshold to between 1 to 0
                      "first_time":time.time() }  # sec   # first time sonic sensor detect object

        self.wait = { "adaptive_loop_d" : 0.05,   # sec    # system loop wait time is adaptive, by this value
                      "adaptive_loop_limit":0.5,   # sec    # system loop wait time limit
                      "mode_cnt" : 0,          # count    # how many times wait mode occur continuously
                      "task_probability":0.01,            # "Wait_Mode_Task" in this random probability
                      "task_min_time" : 30,      # sec    # minimum "Wait_Mode_Task" duration
                      "task_last_time":time.time()}# sec  # last time when "Wait_Mode_Task" occur

        self.keep_talk = {"max": 0,
                          "cur_iter": 0}

        self.base_path = "/home/pi/Desktop/PinoBot/"

        # 3. Objects
        self.HardWare = None
        self.cloud = None
        self.reserved_task = []
        self.task_q = queue.Queue()

        # 4. Init Functions
        boot = Pino_Init(self.base_path)
        self.hardware ,self.cloud = boot.boot()
        self.hardware.write(text="부팅완료!\n 대기중..", led=[0,0,0])
        self.__load_logger()

    def __del__(self):
        try:
            self.log_file.close()
            self.log.removeHandler(self.log_file)
            self.log_consol.close()
            self.log.removeHandler(self.log_consol)
            del self.log
        except:
            pass

        try:
            del self.hardware
            del self.cloud
        except:
            pass

    def reset(self):
        # TODO: Add reset fuction
        pass

    def __load_logger(self):
        # 1 set logger and formatter
        path = self.base_path + "/log/PinoMain.log"
        self.log = logging.getLogger("Boot")
        self.log.setLevel(logging.DEBUG)
        formatter = logging.Formatter('[%(levelname)s] (%(asctime)s : %(filename)s:%(lineno)d) > %(message)s')

        # 2 set file logger
        self.log_file = RotatingFileHandler(filename=path, maxBytes=5 * 1024 * 1024,
                                            mode='w',
                                            encoding='utf-8')
        self.log_file.setFormatter(formatter)
        self.log.addHandler(self.log_file)

        # 3 set consol logger
        self.log_consol = logging.StreamHandler()
        self.log_consol.setFormatter(formatter)
        self.log.addHandler(self.log_consol)

        # 4 logger OK.
        self.log.info("Start BootLoader")
        return 0

    def run(self):
        while True:
            self.main_loop_once()
            time.sleep(self.wait["adaptive_loop_d"])

    def main_loop_once(self):
        """
        pinobot's main loop function

        """
        # 1. check hardware signals
        cur_sensor_state = 0
        volume, distance, serial_msgs = self.hardware.read()
        if serial_msgs is not None:
            # TODO : add event task
            pass
        if volume != self.cur_volume:
            # TODO : change volume
            pass
        if self.detect["distance"] > distance > 4:
            cur_sensor_state = 1

        # 2. do actions by sensor state.
        if self.detect["pre_state"] == 0 and cur_sensor_state == 1:
            # 2.1 object [ 0 -> 1 ] , new object
            # add talk task
            self.detect["first_time"] = time.time()
            self.__add_task("talk")

        elif self.detect["pre_state"] == 1 and cur_sensor_state == 0:
            # 2.2 object [ 1 -> 0 ] , object gone
            if self.sleep['state'] :
                # if in "sleep mode" change to wake mode, and add WakeUp_Event
                self.sleep['state'] = False
                self.__add_task("event", "WakeUp_Event", fail_handler=False) # TODO : TEST

        elif self.detect["pre_state"] == 1 and cur_sensor_state == 1:
            # 2.3 object [ 1 -> 1 ] , object still in


            if self.sleep['state'] and time.time() - self.sleep['task_last_time']> self.sleep['task_min_time']:
                # if already in sleep mode, do random "sleep mode event"
                if random.random() <= self.sleep['task_probability']:
                    self.__add_task("event", "Sleep_Event", fail_handler=False)

            # not sleep mode, change to sleep mode
            elif time.time() - self.detect["first_time"] > self.sleep["enter_limit_time"]:
                self.sleep['state'] = True
                self.__add_task("event", "Sleep_Enter_Event", fail_handler=False)

        else :
            # 2.4 object [ 0 -> 0 ] , wait mode
            self.wait["mode_cnt"] +=1
            # set adaptive wait duration
            if self.wait["adaptive_loop_d"] + 0.01 < self.wait["adaptive_loop_limit"]:
                self.wait["adaptive_loop_d"] += 0.01
            # do random "wait mode event"
            if random.random() <= self.wait['task_probability']:
                self.__add_task("event", "Wait_Event", fail_handler=False)
        self.detect["pre_state"] = cur_sensor_state

        # 3. check Reserved Task list
        for task in self.reserved_task:
            reserve_time = task[0]

            #print("res : ", reserve_time)
            #print("now : ", datetime.datetime.now().astimezone())
            if datetime.datetime.now().astimezone() > reserve_time: # TODO[1] : TEST
                self.__add_task(task_type="event", event_name=task[1], event_parameter=task[2])
                self.reserved_task.remove(task)

        # 4. check Task Q
        # before end all task, don't end mainloop
        # this is also needed for continuous talk
        while self.task_q.qsize() > 0:
            next_task = self.task_q.get()
            self.run_task(next_task)

    def run_task(self, task):
        task_type       = task[0]
        event_name      = task[1]
        event_parameter = task[2]
        fail_handler    = task[3]
        talk_responses = ()
        event_response = None

        # [STEP 1.1] get "talk" response
        if task_type == "talk":
            """
            Description of DialogFlow streaming, 
            
            1. self.cloud.strat_stream() 
                start voice streaming immediately, keep send sound data to Google Server, 
            
            2. self.cloud.get_response() 
                return tuple object, return = (stt_response, chatbot_response, tts_response)
            
            # E1. stt_response is None,
                if can't recognize voice or talking
            
            # E2. stt_response.recognition_result.transcript == ""
                sometimes, if recognize something but it not talking,
                (usually occur when language is not matched..)
            
            # E3. No matched Intent
                if there is no matched intent, 
                Usually dialogFlow automatically set intent to -> "Default Fallback Intent"
                but "Default Fallback Intent" is too broad,
                therefore, in PinoBot make new intent : "Fail_NoMatch_Intent"
            """

            # 1. streaming voice
            self.hardware.write(text="듣는중..", led=[204, 255, 51])
            self.cloud.start_stream()
            talk_responses = self.cloud.get_response()
            self.hardware.write(text="인식중..", led=[0, 0, 0])

            # E1. do not talk anything
            if talk_responses[0] is None:
                # if streaming can't rec talking, return None to Response
                if fail_handler is not False:
                    event_response = self.cloud.send_event("Fail_NotTalk_Intent")
                    task_type = "event"
                else :
                    self.hardware.write(text="Talk Fail", led=[150, 50, 0])
                    return -1

            # E2. do not talk anything
            elif len(talk_responses[0].recognition_result.transcript) == 0:
                # or just cant't rec talk
                if fail_handler is not False:
                    event_response = self.cloud.send_event("Fail_NotTalk_Intent")
                    task_type = "event"
                else :
                    self.hardware.write(text="Talk Fail", led=[150, 50, 0])
                    return -1

            # E3. No matched Intent
            elif talk_responses[1].query_result.intent.display_name == "Default Fallback Intent":
                if fail_handler is not False:
                    #self.__add_task("event", "Fail_NoMatch_Intent", fail_handler=False)
                    task_type = "event"
                else :
                    self.hardware.write(text="Talk Fail", led=[150, 50, 0])
                    return -1
            # No Error
            else :
                self.hardware.write(text="", led=[0, 150, 0])

        # [STEP 1.2] get "event" response
        elif task_type == "event" and event_name is not None:
            """
            Description of DialogFlow Event, 

            1. self.cloud.send_event(event_name, event_parameter)
            call event by event_name(str) and event_parameter(dict)
            responses contain chatbot_response, and tts_response, (no need stt_response)

            # E1. event_response is None,
                not Usually occur, but sometimes happen, therefore we need handler
                
            # E2. No matched Intent
                Most common case, if there is no matched intent
                Usually dialogFlow automatically set intent to -> "Default Fallback Intent"
                but "Default Fallback Intent" is too broad,
                therefore, in PinoBot make new intent : "Fail_NoMatch_Intent"
            
            # E3. event fail case
            """
            event_response = self.cloud.send_event(event_name, event_parameter)
            # E1. unknown error cause response to None
            if not hasattr(event_response,'query_result'):
                if fail_handler is not False:
                    event_response = self.cloud.send_event("Fail_NoMatch_Intent")
                else :
                    self.hardware.write(text=event_name+"\n fail", led=[150, 50, 0])
                    return -1

            # E2. No matched Intent
            elif event_response.query_result.intent.display_name == "Default Fallback Intent":
                if fail_handler is not False:
                    event_response = self.cloud.send_event("Fail_NoMatch_Intent")
                else :
                    self.hardware.write(text=event_name+"\n fail", led=[150, 50, 0])
                    return -1

            # E3. event fail case
            if event_response is None :
                self.hardware.write("fail event \n %s"%event_name)
                return -1

        # [STEP 1.3] ignore invalid event type
        else :
            print("invalid task , ignore")
            return -1

        # [STEP 2.1] Parse query result
        dflow_parameters = {}
        pino_commands = []
        query_result = None
        if task_type == "talk":
            query_result = MessageToDict(talk_responses[1].query_result)
        elif task_type == 'event' and event_response is not None: # TODO find error why event_response= None came to here
            query_result = MessageToDict(event_response.query_result)
        else:
            return -1
        intent_name = query_result['intent']['displayName']

        # [STEP 2.2] Parse DialogFlow PinoBot Parameter
        # TODO intent name matching without upper , lower case
        """
        Description of DialogFlow PinoBot Parameter,
        
        to actuate pinobot in DialogFlow Console, we use action parameter Field.
        in query_result.parameters or  query_result['parameters'], 
        PinoBot Command and Dialogflow original parameters are contain
        
        "Dialogflow original parameters":
        time:                       str -> "2020-08-27T18:44:42+09:00"
        ...
        
        "PinoBot Event Command":
        PinoFutureEventName         str  -> "Fail_NoMatch_Intent"
        PinoFutureEventParameter    dict -> {"para1":"123"} 

        "PinoBot Command" :
        $n_PinoActuate              list  -> [2,10,10,30,40,50]
        $n_PinoLED                  list  -> [50,20, 90]
        $n_PinoSerial               str   -> "asd_ass"
        $n_PinoWait                 float -> 1.2
        $n_PinoShowImage            str   -> "12.jpg"     
        $n_PinoShowText             str   -> "Hello \n world"    
       
        TODO 
        $n_PinoExpress              str   -> "smile"
        $n_PinoPlayWav              str   -> "1.wav"
        
        
        $n is order of command written in Dialogflow Console.
        Due to that, actual "PinoBot Command" is like..
        
        {"1_PinoActuate : "[2,10,10,30,40,50]",
         "2_PinoSerial :  "asdf",
         ...
         "time" : "2020-08-27T18:44:42+09:00",
         "PinoFutureEventName" : "Fail_NoMatch_Intent"
         }
    
        in bellow code, just extract "PinoBot Command" and order it, 
        actual executing "PinoBot Command" is on self.run_cmds 
        
        """

        for action_parameters in query_result['parameters'].keys():
            # split order and "PinoBot Command" name
            check_cmd = action_parameters.split("_")

            if len(check_cmd) != 1:
                # if "_" is contained in parameter name, like.. ("1_PinoCmd" or "a_asdf")
                try:
                    num = ast.literal_eval(check_cmd[0])
                except SyntaxError:
                    self.log.warning("parse event parameter error, in future_event :%s" % action_parameters)
                    continue

                if isinstance(num, int) or isinstance(num, float) :
                    # check first block "1" or "a" is int or float,
                    pino_commands.append([num, check_cmd[1], query_result['parameters'][action_parameters]])
                else :
                    # if first block is not number (like "a") : go to dflow_parameters
                    dflow_parameters[action_parameters] = query_result['parameters'][action_parameters]
            else :
                dflow_parameters[action_parameters] = query_result['parameters'][action_parameters]

        pino_commands.sort(key=lambda x: x[0]) # sort by command order number

        # [STEP 3] Execute PinoBot Parameter
        print("run intent: ",intent_name,"\n cmds :",pino_commands)
        # start actuate in thread
        t1 = threading.Thread(target=self.__execute_pino_commands, args=(intent_name, pino_commands))
        t1.start()

        # start play saying
        if task_type == "talk":
            self.cloud.play_audio(talk_responses[2])
        elif task_type == 'event':
            self.cloud.play_audio(event_response)
        # wait for end
        t1.join()

        if "PinoPlayWav" in pino_commands:
            # TODO : Play wave file
            pass

        # TODO : Extention
        """
        to make user write script and handle custom commands 
        in future 1.5 version, make extention from here
        users write script by dialog parameters and hardware, and can add event

        this also could connect with scratch language
        """
        if "PinoCustomCmd" in dflow_parameters :
            run_pino_custom_cmd(hardware=self.hardware,
                            intent_name=intent_name,
                            dialogflow_parameters=query_result['parameters'])

        self.__run_pino_event_commands(dflow_parameters)
        return 0

    def __add_task(self, task_type, event_name = None, event_parameter=None, fail_handler = True):
        self.log.info("%s %s %s %r"%(task_type, event_name, event_parameter, fail_handler))
        if isinstance(event_parameter,dict):
            self.task_q.put([task_type, event_name, event_parameter, fail_handler])

        elif isinstance(event_parameter,str):
            try:
                parsed_parameter = ast.literal_eval(event_parameter.strip())
            except SyntaxError:
                self.log.warning("parse event parameter error, in future_event :%s" % parsed_parameter)
                parsed_parameter = None
            else :
                if isinstance(parsed_parameter,str):
                    self.log.warning("parse event parameter error:%s"%parsed_parameter)
                    parsed_parameter = None
            self.task_q.put([task_type, event_name, parsed_parameter, fail_handler])

        else :
            self.task_q.put([task_type, event_name, None, fail_handler])

    def __execute_pino_commands(self, intent_name, pino_command):
        for pino_cmd in pino_command:
            self.__run_pino_command(intent_name, pino_cmd)

    def __run_pino_command(self, intent_name, cmd):
        cmd_name = cmd[1]
        cmd_args = cmd[2]

        if cmd_name == "PinoActuate":
            args = None
            servo_time = None
            try:
                args = ast.literal_eval(cmd_args)
                servo_time = float(args[0])
            except:
                self.hardware.write(text="DFlow Error \n %s \n PinoActuate" % intent_name, led=[150, 50, 0])
                return -1
            else:
                if type(args) is not list or type(servo_time) is not float or len(args) < 2:
                    self.hardware.write(text="DFlow Error \n %s \n PinoActuate" % intent_name, led=[150, 50, 0])
                else:
                    self.hardware.write(servo_angle=args[1:], servo_time=servo_time)
                    return 0

        elif cmd_name == "PinoExpress":
            # TODO : actuate prebuild face emotion
            pass

        elif cmd_name == "PinoLED":
            args = None
            try:
                args = ast.literal_eval(cmd_args)
            except:
                self.hardware.write(text="DFlow Error \n %s \n PinoLED" % intent_name, led=[150, 50, 0])
                return -1
            else:
                if type(args) is not list:
                    self.hardware.write(text="DFlow Error \n %s \n PinoLED" % intent_name, led=[150, 50, 0])
                else:
                    self.hardware.write(led=args)
                    return 0

        elif cmd_name == "PinoSerialMsg":
            self.hardware.write(serial_msg=cmd_args)

        elif cmd_name == "PinoShowText":
            self.hardware.write(text=cmd_args)

        elif cmd_name == "PinoShowImage":
            self.hardware.write(image=cmd_args)

        elif cmd_name == "PinoWait":
            args = None
            try:
                args = ast.literal_eval(cmd_args)
            except:
                self.hardware.write(text="DFlow Error \n %s \n PinoWait" % intent_name, led=[150, 50, 0])
                return -1
            else: # TODO, test int type works
                if type(args) is not float or type(args) is not int:
                    self.hardware.write(text="DFlow Error \n %s \n PinoWait" % intent_name, led=[150, 50, 0])
                else:
                    time.sleep(args)
                    return 0

        return 0

    def __run_pino_event_commands(self, dflow_parameters):
        cmd_list = dflow_parameters.keys()


        """
        Description of PinoBot KeepTalk,
        
        if "PinoKeepTalkMax" parameter in intent, pinobot start next talk immediately
        "PinoKeepTalkMax" also means, max number of continuous talk
         
        if "PinoKeepTalkMax" not in next intent, talk stopped
        if called over "PinoKeepTalkMax" value, talk ended and reset
        
        to make continuous talk, use self.run_task("talk") and add talk task.  

        """


        if 'PinoKeepTalkMax' in cmd_list:
            try:
                n_max = ast.literal_eval(dflow_parameters['PinoKeepTalkMax'])
            except SyntaxError:
                self.hardware.write(text="PinoKeepTalkMax \n Error%s  ", led=[50, 250, 0])
                return -1

            if isinstance(n_max,int):
                self.keep_talk['max'] = n_max
                if self.keep_talk['cur_iter'] >= self.keep_talk['max']:
                    print("end keep talk")
                    self.keep_talk['cur_iter'] = 0
                    self.keep_talk['max'] =0
                    return 0
                else :
                    print("end keep talk")
                    self.__add_task("talk")
                    self.keep_talk['cur_iter'] +=1
        else : # reset keep talk
            self.keep_talk['cur_iter'] = 0
            self.keep_talk['max'] = 0


        if 'PinoFutureEventName' in cmd_list and 'PinoFutureEventParameter' in cmd_list:
            event_time = datetime.datetime.strptime(dflow_parameters['time'],
                                                    "%Y-%m-%dT%H:%M:%S%z")  # "2020-08-06T18:00:00+09:00"
            event_name = dflow_parameters['PinoFutureEventName']#'2020-08-31T22:35:46+09:00'
            event_parameter = None
            if isinstance(dflow_parameters['PinoFutureEventParameter'], str):
                try:
                    event_parameter  = ast.literal_eval(dflow_parameters['PinoFutureEventParameter'].strip())
                except SyntaxError:
                    self.log.warning("parse event parameter error, in future_event :%s" % event_parameter)
                    event_parameter = None

                if not isinstance(event_parameter , dict):
                    self.log.warning("parse event parameter error, in future_event :%s" % event_parameter )
                    event_parameter= None

            # TODO : save and load future event in files
            # TODO : sort events by remain times.
            later = str(event_time -datetime.datetime.now().astimezone())
            self.reserved_task.append([event_time, event_name, event_parameter])
            self.hardware.write(text="이벤트 예약 \n %s \n+ %s " % (event_name ,later[:-7]), led=[50, 250, 0])
            self.log.info("add reserved event %s %s %s %s"%(event_time, event_name,later,str(event_parameter)))

def test():
    a = PinoBot()
    a.run()

if __name__ == '__main__':
    test()
    #test()
