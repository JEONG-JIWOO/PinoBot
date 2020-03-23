import RPi.GPIO as GPIO
import time
import sys
import signal

"""
Reference
https://m.blog.naver.com/PostView.nhn?blogId=chandong83&logNo=221155355360


"""

class HC_SR04():
    def __init__(self):
        self.MAX_DISTANCE = 150
        self.TIMEOUT = self.MAX_DISTANCE* 2 * 29.41 

        self.TRIG_Pin = 13 # trigger gpio pin
        self.ECHO_Pin = 12 # echo gpio pin
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.TRIG_Pin, GPIO.OUT) 
        GPIO.setup(self.ECHO_Pin, GPIO.IN)  
        GPIO.output(self.TRIG_Pin, False)

        self.distance = 0

    def __del__(self):
        GPIO.cleanup()
    
    def measure_once(self):
        # 1. send start signal to Trigger pin
        GPIO.output(self.TRIG_Pin, True)
        time.sleep(0.00001)
        GPIO.output(self.TRIG_Pin, False)

        # 2. receive response
        measure_start = time.time()
        pulse_start = 0
        pulse_end = 0

        # 3. wait for first pulse.
        while GPIO.input(self.ECHO_Pin) == 0:
            pulse_start = time.time()
            if ((pulse_start - measure_start)*1000000) >= self.TIMEOUT :
                return 150
    
        # 4. measure time for last pulse.
        measure_start = time.time()
        while GPIO.input(self.ECHO_Pin) == 1:
            pulse_end = time.time()
            if ((pulse_end - pulse_start)*1000000) >=  self.TIMEOUT:
                return 150

        # 5. change time to distance
        self.distance = ( (pulse_end - pulse_start) * 17001) # 1000000/2 / 29.41
        return self.distance


def test():
    sensor = HC_SR04()
    while 1:
        time.sleep(0.1)
        distance = sensor.measure_once()
        if distance > 0:
            print(distance)

if __name__ == '__main__':
    test()
