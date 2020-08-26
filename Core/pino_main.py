#!/usr/bin/env python3.7

import time, random , queue

from Core.pino_init import Pino_Init
import ast , datetime

from google.protobuf.json_format import MessageToDict
import threading


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


        # 3. Objects
        self.HardWare = None
        self.cloud = None
        self.reserved_task = []
        self.task_q = queue.Queue()

        """
        self.stt_response = None
        self.chatbot_response = None
        self.tts_response = None
        """

        # 4. Init Functions
        Boot = Pino_Init()
        self.hardware ,self.cloud = Boot.boot()

    def test(self):
        print("tested")
        #del self.hardware
        self.cloud.start_stream()
        stt_response, chatbot_response, tts = self.cloud.get_response()
        if stt_response is not None and chatbot_response is not None:
            print("[Q] : %s " % stt_response.recognition_result.transcript)
            print("[A] : accuracy:%0.3f | %s " % (chatbot_response.query_result.intent_detection_confidence,
                                                  chatbot_response.query_result.fulfillment_text))
        self.cloud.play_audio(tts)

    def run(self):
        while True:
            # try:
            self.main_loop_once()
            time.sleep(self.wait["adaptive_loop_d"])
            # except:

    # TODO[1] : TEST
    def add_task(self,task_type, event_name = None, event_parameter="",fail_handler = True):
        if event_parameter == "":
            event_parameter = None
        else :
            #
            print("TODO : Parse event parameter str to dict")
            event_parameter = None
        self.task_q.put([task_type,event_name,event_parameter,fail_handler])

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
        if self.detect["distance"] > distance > 4:
            cur_sensor_state = 1
        print(distance," " , self.detect["pre_state"], cur_sensor_state)

        # 2. do actions by sensor state.
        if self.detect["pre_state"] == 0 and cur_sensor_state == 1: # TODO[1] : TEST
            # 2.1 object [ 0 -> 1 ] , new object
            # add talk task
            self.detect["first_time"] = time.time()
            print("start talk")
            self.add_task("talk")

        elif self.detect["pre_state"] == 1 and cur_sensor_state == 0: # TODO[1] : TEST
            # 2.2 object [ 1 -> 0 ] , object gone
            if self.sleep['state'] :
                self.sleep['state'] = False
            print("Wake Up!")

        elif self.detect["pre_state"] == 1 and cur_sensor_state == 1: # TODO[1] : TEST
            # 2.3 object [ 1 -> 1 ] , object still in
            print("check sleep mode")

            # if already in sleep mode
            if self.sleep['state'] and time.time() - self.sleep['task_last_time']> self.sleep['task_min_time']: # TODO[1] : TEST
                print("in sleep, add sleep event random 1%")
                if random.random() <= self.sleep['task_probability']: # TODO[1] : TEST
                    self.add_task("event","Sleep_Event",fail_handler=False)

            # not sleep mode
            elif time.time() - self.detect["first_time"] > self.sleep["enter_limit_time"]: # TODO[1] : TEST
                self.sleep['state'] = True
                print("now go to sleep mode,")
                self.add_task("event", "Sleep_Enter_Event",fail_handler=False)

        else : # TODO[1] : TEST
            print("waiting..")
            # 2.4 object [ 0 -> 0 ] , wait mode
            self.wait["mode_cnt"] +=1
            # set adaptive wait duration
            if self.wait["adaptive_loop_d"] + 0.01 < self.wait["adaptive_loop_limit"]: # TODO[1] : TEST
                self.wait["adaptive_loop_d"] += 0.01
            if random.random() <= self.wait['task_probability']: # TODO[1] : TEST
                self.add_task("event", "Wait_Event", fail_handler=False)
        self.detect["pre_state"] = cur_sensor_state

        # 3. check Reserved Task list
        print(self.reserved_task)
        for task in self.reserved_task:
            reserve_time = task[0]
            if datetime.datetime.now() < reserve_time: # TODO[1] : TEST
                self.add_task(task_type="event", event_name=task[1], event_parameter=task[2])
                self.reserved_task.remove(task)

        # 4. check Task Q
        if self.task_q.qsize()>0:
            next_task = self.task_q.get()
            self.run_task(next_task)

    def run_task(self, task):
        task_type       = task[0]
        event_name      = task[1]
        event_parameter = task[2]
        fail_handler    = task[3]

        responses = ()
        # 1. select talk or event
        if task_type == "talk":
            # 1.1 talk task
            self.hardware.write(text="듣는중..", led=[204, 255, 51])
            self.cloud.start_stream()
            responses = self.cloud.get_response()
            self.hardware.write(text="I Heard !", led=[0, 0, 0])

        elif task_type == "event" and event_name is not None:
            # 1.2 event task
            # TODO[WIP] execute event
            event_response = self.cloud.send_event(event_name, event_parameter)
            responses = (event_response,None,None)
        else :
            print("invalid task , ignore")
            return -1

        # TODO[1] : TEST
        # 2. check response in valid
        responses = self.check_response(responses,task_type, fail_handler)
        if responses is None :
            # if fail_handling is False, just show Error Message and quite task
            if task_type == "talk":
                self.hardware.write(text="Talk Fail", led=[150, 50, 0])
            elif task_type == "event":
                self.hardware.write(text="Event Fail\n%s" % event_name, led=[150, 50, 0])
            return 0

        # 3. Parse Response
        intent_name, pino_cmds, dflow_parameters,tts_response = self.parse_response(responses,task_type)

        print("run intent: ",intent_name)
        # 4,1 start actuate in thread
        t1 = threading.Thread(target=self.run_cmds, args=(intent_name, pino_cmds))
        t1.start()

        # 4.2 start play saying
        self.cloud.play_audio(tts_response)
        t1.join()

        # 5. if there are future event, add it
        self.add_future_event(intent_name, dflow_parameters)
        # TODO : if context exist, make loop
        return 0

    def check_response(self,responses,task_type, fail_handler):
        fail_response = None
        state = 0

        if task_type == 'event' :
            # 1. case A, responses is event response
            if hasattr(responses[0] ,'query_result'):
                return responses
            else :
                fail_response = self.cloud.send_event("FailNoMatchIntent")
                return fail_response

        else :
            # 2. case B, responses is voice response
            if responses[0] is None: # stt_response
                # 2.1 stt fail
                state = -1
                fail_response = self.cloud.send_event("FailHearIntent")

            elif len(responses[0].recognition_result.transcript) == 0:
                # 2.2 stt ok but talk nothing
                state = -2
                fail_response = self.cloud.send_event("FailNotTalkIntent")

            elif responses[2].query_result.intent.display_name == "Default Fallback Intent":
                # 2.3 stt done but no matching intent
                state = -3
                fail_response = self.cloud.send_event("FailNoMatchIntent")
            else :
                # 2.4 nothing fail, success.
                return responses

            # 3. check Fail Event response
            if state != 0 and fail_response is not None and fail_handler == True:
                return fail_response,fail_response,fail_response
            else :
                return None

    def parse_response(self,responses,task_type):
        tts_response = None
        query_result = None
        if task_type == "talk":
            query_result = MessageToDict(responses[1].query_result)
            tts_response = responses[2]
        elif task_type == 'event':
            query_result = MessageToDict(responses[0].query_result)
            tts_response = responses[0]
        else :
            return None,None,None,None

        intent_name = query_result['intent']['displayName']
        dflow_parameters = {}
        pino_cmds = []

        # parse answer
        for action_parameters in query_result['parameters'].keys():
            check_cmd = action_parameters.split("_")
            if len(check_cmd) == 1:
                dflow_parameters[action_parameters] = query_result['parameters'][action_parameters]
            else:
                num = ast.literal_eval(check_cmd[0])
                pino_cmds.append([num, check_cmd[1], query_result['parameters'][action_parameters]])
        pino_cmds.sort(key=lambda x: x[0])
        return intent_name, pino_cmds, dflow_parameters, tts_response


    def add_future_event(self, intent_name, dflow_parameters):
        # TODO dflow_parameters are string, change to dict
        print(dflow_parameters)
        parameters = ast.literal_eval(dflow_parameters)
        if intent_name == "Default Fallback Intent":
            return 0
        elif "time" not in parameters.keys() or "PinoFutureEvent" not in parameters.keys():
            self.hardware.write(text="DFlow Error \n %s \n PinoFutureEvent" % intent_name, led=[150, 50, 0])
            return -1
        elif "EVENT" not in parameters["PinoFutureEvent"].keys():
            self.hardware.write(text="DFlow Error \n %s \n PinoFutureEvent" % intent_name, led=[150, 50, 0])
            return -2
        else:
            # TODO[1] : TEST
            d = dflow_parameters["PinoFutureEvent"]["EVENT"]
            event_time = datetime.datetime.strptime(dflow_parameters['time'],
                                                    "%Y-%m-%dT%H:%M%S")  # "2020-08-06T18:00:00+09:00"
            event_name = d.pop["EVENT"]
            event_parameter = None
            if not d:
                event_parameter = d
            self.reserved_task.append([event_time, event_name, event_parameter])
            self.hardware.write(text="이벤트 예약 \n %s  " % intent_name, led=[50, 250, 0])
            print("future event added")

    def run_cmds(self, intent_name, pino_cmds):
        for pino_cmd in pino_cmds:
            self.command(intent_name, pino_cmd)

    def command(self, intent_name, cmd):
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
            else:
                if type(args) is not float:
                    self.hardware.write(text="DFlow Error \n %s \n PinoWait" % intent_name, led=[150, 50, 0])
                else:
                    time.sleep(args)
                    return 0

        return 0

def test():
    a = PinoBot()
    a.run()

if __name__ == '__main__':
    test()
