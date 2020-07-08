import spidev
import time

class Pino_UART():
    def __init__(self,port="COM0",baud_rate = 115200):
        # 1. Static Variables



        # 2. variables




        # 3. Objects



        # 4. Init Functions



    def __del__(self):



    def reset(self):
        # 1. check last reset time,
        #    only can reset after 1min after last reset
        if (time.time() - self.last_reset_time) < 60:
            return 0

        # 2. if self.serial exists..
        if self. is not None:



        # 3. refresh last reset time
        self.last_reset_time = time.time()

        # 4. re open Serial
        try:

        except Exception as E:
            self.last_exception = str(E)
            return -1

    def write(self,data):
        # 1. try to send
        try :
            self..write()
        # 2. Fail to send data
        except Exception as E :
            self.last_exception = str(E)
            self.reset()
            return -1
        # 3. Success to send data
        else :
            return 0

