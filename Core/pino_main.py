#!/usr/bin/env python3.7

#from Hardware.v1 import HardwareV1
#from Cloud.Google import pino_dialogflow
import enum , time, random
from threading import Lock, Thread

class STATE(enum.Enum):
    BOOT = 0
    IDLE = 1
    WALL_FACE = 2
    VOICE_REC = 3

class PinoBot():
    def __init__(self):
        
        # 0. common variablev
        self.state = STATE.BOOT
        self.lock = Lock()
        # 1. init hareware and thread variable,
        # be careful to use, without "LOCK", it can cause segemtation error
        self.react_distance = 20
        self.wall_threshold_time = 30
        self.sensor_state = 0  # -1 : facing object over self.wall_threshold time
                               #  0 : no object
                               #  1 : measure object
        self.HardWare = None

        # 2. init cloud

        
        # 3. do some boot process
        self.boot_process()
        pass

    def ini_parser(self):
        """
        [WIP] write ini pareser, 
        
        ini component:
        1. google key path and name,
        2. dialogflow project name, 
        3. wifi name and password
        4. volume,
        5. motor index

        """
        
        pass

    def boot_process(self):
        
        """
        [WIP]BOOT PROCESS
        1. parsing ini
        2. check hardware, i2c channel, and sonic sensor, if failed, show [HARDWARE ERROR]
        3. check wifi connection, if failed, try to connect 3 times and if failed, show [WIFI ERROR]
        4. check cloud connection, if failed, try to connect 3 times and if failed, show [CLOUD ERROR] 
        5. if all completed. show [READY]" message
        6. start sensor thread

        """

        # 1. parsing ini
        self.ini_parser()
        
        # 2. check hardware, i2c channel, and sonic sensor, if failed, show [HARDWARE ERROR]
        """
        try: 
            self.HardWare = HardwareV1()
        except Exception as e: 
            print(e)
        """

        # 3. check wifi connection, if failed, try to connect 3 times and if failed, show [WIFI ERROR]
        
        # 4. check cloud connection, if failed, try to connect 3 times and if failed, show [CLOUD ERROR] 
        """
        DIALOGFLOW_PROJECT_ID = 'a2-bwogyf'
        DIALOGFLOW_LANGUAGE_CODE = 'ko'
        GOOGLE_APPLICATION_CREDENTIALS = '/home/pi/PinoBot/Keys/a2-bwogyf-c40e46d0dc2b.json'

        self.Cloud = pino_dialogflow.PinoDialogFlow(DIALOGFLOW_PROJECT_ID,
                                                    DIALOGFLOW_LANGUAGE_CODE,
                                                    GOOGLE_APPLICATION_CREDENTIALS)
        
        """   
        
        # 5. if all completed. show [READY]" message
        
        self.sensor_t = Thread(target=self.sensor_thread)
        self.sensor_t.start()

        self.state = STATE.IDLE

    def sensor_thread(self):
        d = 0
        s_state = 0
        T_LIMIT = 0

        with  self.lock:
            d = self.react_distance
            T_LIMIT = self.wall_threshold_time 
        
        while True:
            with  self.lock:
                #distance = self.HardWare.read_sonic()
                distance = random.uniform(12,19)
                print("d: %0.2f"%distance)

                # 1. onject  [out -> in]
                if distance < d and s_state == 0:
                    s_state = 1
                    detect_time_0 = time.time()

                # 2. object [in -> out]
                elif distance > d and s_state == 1:
                    s_state = 0

                # 3. object [Measure WALL] is still in and over threathold time:
                elif time.time() - detect_time_0 > T_LIMIT :
                    s_state = -1

                # 4. object [Escape WALL]
                elif distance > d and s_state == -1: 
                    s_state = 0

                self.sensor_state = s_state
            time.sleep(0.5)

    def stream_voice(self):
        """
        [WIP] voice recognization code
        """
        time.sleep(6)
        stt_response = None
        chatbot_response = None
        return stt_response, chatbot_response

    def send_event(self,Event):
        """
        [WIP] Cloud event send code
        """
        time.sleep(1)
        response = None
        return response

    def do_action(self,action):
        """
        [WIP] do some actions..

        """
        with  self.lock:
            """ control hardware"""    
            pass 

        pass
    
    
    def main_loop(self):    

        # 0. BOOT 
        if self.state == STATE.BOOT:
            print("BOOT ON")
            action = self.send_event("BOOT")
            self.do_action(action)            
            self.state = STATE.IDLE


        # 1. IDLE
        elif self.state == STATE.IDLE :
            # 1.1 Get sonsor state with thread Lock
            print("IDLE")

            sensor_state = -2
            with  self.lock:
                sensor_state = self.sensor_state
            
            # 1.2 change state and do action
            if sensor_state == 1:
                self.state = STATE.VOICE_REC
                print("[GO] VOICE REC")

            elif sensor_state == 0:
                action = self.send_event("IDLE")
                self.do_action(action)

            elif sensor_state == -1:
                self.state = STATE.WALL_FACE
                print("[GO] WALL FACE")

        # 2. WALL_FACE
        elif self.state == STATE.WALL_FACE :
            # 2.1 do wall face action 
            print("WALL FACE")
            action = self.send_event("WALL_FACE")
            self.do_action(action)
            
            # 2.2 Get sonsor state with thread Lock
            sensor_state = -2
            with  self.lock:
                sensor_state = self.sensor_state
            
            if sensor_state == 0:
                self.state = STATE.IDLE
                print("[GO] IDLE")
            
        # 3. VOICE_REC
        elif self.state == STATE.VOICE_REC:
            # 3.1 do stream voice and, get [STT] and [CHATBOT] response
            stt , chatbot = self.stream_voice()
            
            # 3.2 fail to recognize user voice
            if stt == None:
                print("NO HEAR")
                action = self.send_event("NOT_HEAR")
                self.do_action(action)

            # 3.3 sucess and get chatbot response
            else :
                print(" DO SOTHING ")
                self.do_action(chatbot)

            # 3.4 back to idle            
            self.state = STATE.IDLE

        
def test():
    a = PinoBot()
    while True:
        a.main_loop()
        time.sleep(0.5)
test()