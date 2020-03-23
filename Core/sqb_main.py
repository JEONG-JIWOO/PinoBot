#!/usr/bin/env python3.7

from Hardware.v1 import HardwareV1


class Pinobot():
    def __init__(self):
        self.hardware = HardwareV1()
        #self.hardware.write(text="init hardware")
        pass
    
    def boot(self):
        pass
    
    def main_loop(self):
        pass

a = Pinobot()