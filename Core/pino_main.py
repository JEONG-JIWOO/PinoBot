#!/usr/bin/env python3.7

from Hardware.v1 import HardwareV1

class Pinobot():
    def __init__(self):
        self.HardWare = HardwareV1()
        self.HardWare.write(text="init hardware v1")
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