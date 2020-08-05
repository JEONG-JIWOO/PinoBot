#!/usr/bin/env python3.7

import time, random , queue

from Core.Utils.pino_utils import Pino_Utils
import ast
from google.protobuf.json_format import MessageToDict
import threading

class Task:
    def __init__(self, hardware, cloud, reserved_task):
        self.type = "talk"
        self.reserved_task = reserved_task
        self.cloud = cloud
        self.hardware = hardware

        self.stt_response = None
        self.chatbot_response= None
        self.tts_response= None

        self.event_name = None
        self.event_parameter = None

    def __del__(self):
        del self.stt_response
        del self.chatbot_response
        del self.tts_response

    def run(self):

        # 1. select talk or event
        if self.type == "talk":
            self.hear()
        elif self.type == "event":
            self.event()

        # 2. check response in valid
        self.check_response()
        intent_name, pino_cmds ,dflow_parameters = self.parse_response()

        # 3,1 start actuate in thread
        t1 = threading.Thread(target=self.run_cmds,args=(intent_name, pino_cmds))
        t1.start()

        time.sleep(5) #test code

        # 3.2 start play saying
        self.cloud.play_audio(self.tts_response)
        t1.join()

        # 4. if there are future event, add it
        self.add_future_event(intent_name, dflow_parameters)

        # TODO : if context exist, make loop


    def hear(self):
        # 1. start stream
        self.hardware.write(text="듣는중..", led=[204, 255, 51])
        self.cloud.start_stream()

        # 2. get Response
        self.stt_response, self.chatbot_response, self.tts_response = self.cloud.get_response()
        self.hardware.write(text="I Heard !", led=[0, 0, 0])

    def event(self):
        if self.event_name is not None:
            # TODO execute event
            print("run event!")

    def check_response(self):
        fail_response = None
        state =  0
        # 3. result check and if talk failed, call Fail events
        if self.stt_response is None:
            # 3.1 stt fail
            state = -1
            fail_response = self.cloud.send_event("FAIL_Hear")

        elif len(self.stt_response.recognition_result.transcript) == 0:
            # 3.2 stt ok but talk nothing
            state = -2
            fail_response = self.cloud.send_event("FAIL_NotTalk")

        elif self.chatbot_response.query_result.intent.display_name == "Default Fallback Intent":
            # 3.3 stt done but no matching intent
            state = -3
            fail_response = self.cloud.send_event("FAIL_NoMatchEvent")

        # 4. case Fail Event
        if state != 0 and fail_response is not None:
            # 4.1 Fail Event is Invalid , Due to Intent not existing
            if fail_response.query_result.intent.display_name == "Default Fallback Intent":
                # 4.2 Show ERROR message to LCD
                if state == -1:
                    self.hardware.write(text="DFlow Error \n FAIL_Hear \n not Exist", led=[150, 50, 0])
                elif state == -2:
                    self.hardware.write(text="DFlow Error \n FAIL_NotTalk \n not Exist", led=[150, 50, 0])
                elif state == -3:
                    self.hardware.write(text="DFlow Error \n FAIL_NoMatchEvent \n not Exist", led=[150, 50, 0])
                time.sleep(1)

            # 4.2 return result
            self.stt_response = fail_response
            self.chatbot_response = fail_response
            self.tts_response = fail_response
            return -1
        return 0


    def parse_response(self):
        # parse response
        query_result = MessageToDict(self.chatbot_response.query_result)
        intent_name = self.chatbot_response.query_result.intent.display_name
        dflow_parameters = {}
        pino_cmds =[]

        # parse answer
        for action_parameters in query_result['parameters'].keys():
            check_cmd = action_parameters.split("_")
            if len(check_cmd) == 1:
                dflow_parameters[action_parameters]=query_result['parameters'][action_parameters]
            else:
                num = ast.literal_eval(check_cmd[0])
                pino_cmds.append([num,check_cmd[1],query_result['parameters'][action_parameters]])
        pino_cmds.sort(key=lambda x: x[0])
        return intent_name, pino_cmds ,dflow_parameters


    def add_future_event(self,intent_name,dflow_parameters):
        if intent_name == "Default Fallback Intent":
            return 0
        elif "time" not in dflow_parameters.keys() or "PinoFutureEvent" not in dflow_parameters.keys():
            self.hardware.write(text="DFlow Error \n %s \n PinoFutureEvent" % intent_name, led=[150, 50, 0])
            return -1
        else:
            self.reserved_task.append([dflow_parameters['time'], dflow_parameters["PinoFutureEvent"]])
            self.hardware.write(text="이벤트 예약 \n %s  "% intent_name, led=[50, 250, 0])
            print("future event added")

    def run_cmds(self,intent_name , pino_cmds):
        for pino_cmd in pino_cmds:
            self.command(intent_name, pino_cmd)

    def command(self,intent_name,cmd):

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
                    self.hardware.write(text="DFlow Error \n %s \n PinoActuate"%intent_name, led=[150, 50, 0])
                else :
                    self.hardware.write(servo_angle=args[1:],servo_time=servo_time)
                    return 0

        elif cmd_name =="PinoExpress":
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
                    self.hardware.write(text="DFlow Error \n %s \n PinoLED"%intent_name, led=[150, 50, 0])
                else :
                    self.hardware.write(led=args)
                    return 0

        elif cmd_name == "PinoSerialMsg":
            self.hardware.write(serial_msg = cmd_args)

        elif cmd_name == "PinoShowText":
            self.hardware.write(text = cmd_args)

        elif cmd_name == "PinoShowImage":
            self.hardware.write(image = cmd_args)

        elif cmd_name == "PinoWait":
            args = None
            try:
                args = ast.literal_eval(cmd_args)
            except:
                self.hardware.write(text="DFlow Error \n %s \n PinoWait" % intent_name, led=[150, 50, 0])
                return -1
            else:
                if type(args) is not float:
                    self.hardware.write(text="DFlow Error \n %s \n PinoWait"%intent_name, led=[150, 50, 0])
                else :
                    time.sleep(args)
                    return 0

        return 0



class PinoBot:
    def __init__(self):
        # 0. Argument
        # 1. Static Variables

        # 2. variables
        self.cur_volume = 0                               # current speaker volume rate [ 0 ~ 10 ]

        self.sleep = {"state":False,                      # "Sleep_Mode" state, True or False
                      "enter_limit_time":60, # sec        # how much time sensor detect object, change to "Sleep_Mode"
                      "task_ratio":0.01,                  # "Sleep_Mode_Task" in this random probability
                      "task_min_time" : 30,  # sec        # minimum "Sleep_Mode_Task" duration
                      "task_last_time":time.time() }# sec # last time when "Sleep_Mode_Task" occur

        self.detect ={"pre_state":0,                      # last sensor state, 1: in , 0: out
                      "distance":50, # cm                 # sonic sensor threshold to between 1 to 0
                      "first_time":time.time() }  # sec   # first time sonic sensor detect object

        self.wait = { "adaptive_loop_d" : 0.1,   # sec    # system loop wait time is adaptive, by this value
                      "adaptive_loop_limit":1,   # sec    # system loop wait time limit
                      "mode_cnt" : 0,          # count    # how many times wait mode occur continuously
                      "task_ratio": 0.01,                 # "Wait_Mode_Task" in this random probability
                      "task_min_time" : 30,      # sec    # minimum "Wait_Mode_Task" duration
                      "task_last_time":time.time()}# sec  # last time when "Wait_Mode_Task" occur

        # 3. Objects
        self.HardWare = None
        self.cloud = None
        self.reserved_task = []
        self.task_q = queue.Queue()

        # 4. Init Functions
        Boot = Pino_Utils()
        self.hardware ,self.cloud = Boot.boot()
        self.TIME_OUT = int(Boot.config['GCloud']['time_out'])

    def run(self):
        while True:
            # try:
            self.main_loop_once()
            time.sleep(self.wait["adaptive_loop_d"])
            # except:

    def main_loop_once(self):

        # 1. check hardware signals
        cur_sensor_state = 0
        volume, distance, serial_msgs = self.hardware.read()
        if serial_msgs is not None:
            # TODO : add event task
            pass
        if volume != self.cur_volume:
            # TODO : change volume
            pass
        if distance < self.detect["distance"]:
            cur_sensor_state = 1

        # 2. do actions by sensor state.
        if self.detect["pre_state"] == 0 and cur_sensor_state == 1:
            # 2.1 object [ 0 -> 1 ] , new object
            # add talk task
            self.detect["first_time"] = time.time()
            print("talk")
            talk_task = Task(self.hardware,self.cloud,self.reserved_task)
            self.task_q.put(talk_task)

        elif self.detect["pre_state"] == 1 and cur_sensor_state == 0:
            # 2.2 object [ 1 -> 0 ] , object gone
            if self.sleep['state'] :
                self.sleep['state'] = False
            print("Wake Up!")

        elif self.detect["pre_state"] == 1 and cur_sensor_state == 0:
            # 2.3 object [ 1 -> 1 ] , object still in
            print("check sleep mode")

            # if already in sleep mode
            if self.sleep['state'] and time.time() - self.sleep['task_last_time']> self.sleep['task_min_time']:
                print("in sleep, add sleep event random 1%")
                # TODO : add sleep task by probability

            # not sleep mode            elif time.time() - self.detect["first_time"] > self.sleep["enter_limit_time"]:

                self.sleep['state'] = True
                print("now go to sleep mode,")
                # TODO : add sleep move enter task

        else :
            # 2.4 object [ 0 -> 0 ] , wait mode
            self.wait["mode_cnt"] +=1
            # set adaptive wait duration
            if self.wait["adaptive_loop_d"] + 0.01 < self.wait["adaptive_loop_limit"]:
                self.wait["adaptive_loop_d"] += 0.01
            # TODO : add wait task by probability
        self.detect["pre_state"] = cur_sensor_state

        # 3. check Reserved Task list
        print(self.reserved_task)

        # 4. check Task Q
        if self.task_q.qsize()>0:
            next_task = self.task_q.get()
            next_task.run()

def test2():
    Boot = Pino_Utils()
    hardware, cloud = Boot.boot()
    reserved_task = []
    while True:
        a = Task(hardware, cloud,reserved_task)
        a.run()
        time.sleep(0.5)

def test():
    a = PinoBot()
    a.run()

if __name__ == '__main__':
    test2()

