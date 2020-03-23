#!/usr/bin/env python3.7
from gpiozero import  Button 

class Switch():
    
    def __init__(self, GPIO_NAME):
        self._SW = Button(GPIO_NAME)
        self.state = False

    def read_once(self):
        new_state = self._SW.is_pressed
        if self.state != new_state:
            self.state = new_state
            if new_state == True:
                return 1
            else:
                return 0
        else: 
            return -1