#!/usr/bin/env python3.7

from Hardware.v1 import HardwareV1
#from Cloud.Google import pino_dialogflow
import enum , time
from threading import Lock, Thread
from queue import Queue

class STATE(enum.Enum):
    BOOT = 0
    IDLE = 1
    WAIT = 2

    WALL_FACE_START = 10
    WALL_FACE = 11

    VOICE_REC = 20
    NOT_HEAR = 30
    RESPONSE = 31


class PinoBotHardware(threading.Thread):

    def __init__(self):
        self.HardWare = HardwareV1()
        self.HardWare.write(text="init hardware v1")
        self.HardWare_lock = Lock()
        
        self.react_distance = 20
        self.wall_threshold_time = 40
 
        self.hw_state = STATE.IDLE
        self.sensor_state = False # False : object in distance, True: object out of distance

    def sync_state(self,state_q):
        state_q.put(state)
        return 

    def read_sensor(self):
        changed = 0
        pre_state = self.sensor_state
        distance = self.HardWare.read_sonic()

        # 1. onject  [out -> in]
        if distance < self.react_distance and pre_state = False:
            self.sensor_state = True
            changed = 1

        # 2. object [in -> out]
        elif distance > self.react_distance and pre_state = True:
            self.sensor_state = False
            changed = -1

        # 3. state same;
        # pass
        return changed 

    def run(self,cmd_q, state_q, stop_signal):
        detect_time_0 = time.time()
    
        while stop_signal.qsize() < 1:
            """
            STATE
            hardware: IDLE -> VOICE_REC ->              WAIT             -> IDLE  
            cloud :                     -> VOICE_REC -> RESPONSE -> IDLE 

            hardware: IDLE -> WALL_FACE_START ->            WAIT  -> IDLE  
            cloud :                           -> WALL_FACE               -> IDLE
            """

            # 0. COMMON, ACTION
            self.lock.acquire(timeout = 1):
            changed = self.read_sensor()

            # 1. IDLE MODE action
            if self.hw_state == STATE.IDLE : 

                # 1.1 GOTO VOICE_REC
                # first detect, refresh detect_time
                if changed == 1 and time.time() - detect_time_0 < self.wall_threshold_time :
                    detect_time_0 = time.time()  # refresh detect time
                    self.hw_state = STATE.VOICE_REC # change state, and sync
                    self.sync_state(state_q)
                    self.hw_state = STATE.WAIT
                    
                # 1.2 GOTO WALL_FACE_START
                # long detect, think as sensor facing wall, 
                elif changed == 1  :
                    self.hw_state = STATE.WALL_FACE_START
                    self.sync_state(state_q)
                    self.hw_state = STATE.WALL_FACE

                # 1.3 stay  IDLE MODE
                # do nothing, pass

            # 2. WAIT MODE
            # wait. cloud state, just refresh 
            elif self.hw_state == STATE.WAIT:
                if not cmd_q.empty():
                    self.hw_state = cmd_q.get()

            # 3. WALL_FACE MODE
            elif self.hw_state == STATE.WALL_FACE:
                if changed == -1:
                    self.hw_state =  STATE.IDLE
                    self.sync_state(state_q)

            self.lock.release()
            time.sleep(0.5)

class PinoBotCloud():
    def __init__(self):
        
        self.state = STATE.BOOT
                """
        DIALOGFLOW_PROJECT_ID = 'a2-bwogyf'
        DIALOGFLOW_LANGUAGE_CODE = 'ko'
        GOOGLE_APPLICATION_CREDENTIALS = '/home/pi/PinoBot/Keys/a2-bwogyf-c40e46d0dc2b.json'

        self.Cloud = pino_dialogflow.PinoDialogFlow(DIALOGFLOW_PROJECT_ID,
                                                    DIALOGFLOW_LANGUAGE_CODE,
                                                    GOOGLE_APPLICATION_CREDENTIALS)
        
        """
        self.boot_process()
        pass

    def boot_process(self):
        
        """
        do some boot process...
        
        """
        print("boot finish!")
        self.state = STATE.IDLE
        pass

    def main_loop(self):
        
        while True: 
            
        if (self.state == STATE.IDLE):
            if distance < self.react_distance :
                self.state = STATE.VOICE_REC
                self.check_wall()
            else :
                pass
            return 0 

        elif (self.state == STATE.WALL_FACE_START) :
            print("[WALL FACE ] get the wall out! ")
            time.sleep(2)
            self.state = STATE.WALL_FACE
            return 0

        elif (self.state == STATE.WALL_FACE) :
            if distance >  self.react_distance :
                self.state = STATE.IDLE
            else :
                pass
            return 0
        
        elif (self.state == STATE.VOICE_REC): 
            print("start voice rec!")
            time.sleep(5)
            self.state = STATE.RESPONSE
            return 0
        
        elif (self.state == STATE.RESPONSE): 
            print("response !")
            time.sleep(5)
            self.state = STATE.IDLE
            return 0
        
def test():
    a = Pinobot()
    while True:
        a.main_loop()
        time.sleep(0.5)

test()