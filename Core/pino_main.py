#!/usr/bin/env python3.7

from Hardware.v1 import HardwareV1
from Cloud.Google import pino_dialogflow

class Pinobot():
    def __init__(self):
        self.HardWare = HardwareV1()
        self.HardWare.write(text="init hardware v1")

        DIALOGFLOW_PROJECT_ID = 'a2-bwogyf'
        DIALOGFLOW_LANGUAGE_CODE = 'ko'
        GOOGLE_APPLICATION_CREDENTIALS = '/home/pi/PinoBot/Keys/a2-bwogyf-c40e46d0dc2b.json'

        self.Cloud = pino_dialogflow.PinoDialogFlow(DIALOGFLOW_PROJECT_ID,
                                                    DIALOGFLOW_LANGUAGE_CODE,
                                                    GOOGLE_APPLICATION_CREDENTIALS)
        pass
    
    def boot(self):
        pass
    
    def main_loop(self):
        distance = self.HardWare.read_sonic()

        text = str(round(distance))
        self.HardWare.write(text=text)



def test():
    a = Pinobot()
    while True:
        a.main_loop()

test()