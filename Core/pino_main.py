#!/usr/bin/env python3.7

from Hardware.v1 import HardwareV1
#from Cloud.Google import pino_dialogflow
import enum , time
#import threading
#from queue import Queue

class STATE(enum.Enum):
    BOOT = 0
    IDLE = 1

    WALL_FACE_START = 10
    WALL_FACE = 11

    VOICE_REC = 20
    NOT_HEAR = 30
    RESPONSE = 31
    

class Pinobot():
    def __init__(self):
        
        self.state = STATE.BOOT
        self.react_distance = 20
        self.sensor_record = []
        self.wall_d_treshold = 60

        self.HardWare = HardwareV1()
        self.HardWare.write(text="init hardware v1")

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
    
    def check_wall(self):
        l = len(self.sensor_record)
        if  l < 2:
            return 0

        wall_sum = 0.0

        for i in range(l-1) :
            d0,t0 = self.sensor_record[i]
            d1,t1 = self.sensor_record[i+1]
            
            if d0 < self.react_distance :
                d0 = 1
            else :
                d0 = 0

            if d1 < self.react_distance :
                d1 = 1
            else :
                d1 = 0

            wall_sum += (d0+d1)/2 * (t1-t0)


        print(self.sensor_record)
        print("d_rec : %0.3f"%wall_sum)            
        
        if wall_sum > self.wall_d_treshold:
            self.state = STATE.WALL_FACE


    def main_loop(self):
        distance = self.HardWare.read_sonic()
        self.sensor_record.append([distance,time.time()])
        if len(self.sensor_record) > 20 :
            del self.sensor_record[0]
        print(distance)

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