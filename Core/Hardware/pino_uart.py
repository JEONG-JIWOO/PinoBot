import serial
from serial import SerialException
import time

class Pino_UART:
    """
    A. con & deconstruct
    """
    def __init__(self,port="/dev/ttyAMA0",baud_rate = 115200):
        # 0. Argument
        self.port = port
        self.baud = baud_rate

        # 1. Static Variables

        # 2. variables
        self.last_reset_time = 0
        self.last_exception = ""
        self.received_msg = ""

        # 3. Objects
        self.serial = None

        # 4. Init Functions
        self.reset()

    def __del__(self):
        # noinspection PyBroadException
        try:
            self.serial.close()
            del self.serial
        except:
            pass

    """
    B. reset 
    """
    def reset(self):
        # 1. check last reset time,
        #    only can reset after 1min after last reset
        if (time.time() - self.last_reset_time) < 60:
            return 0

        # 2. if self.serial exists..
        if self.serial is not None:
            self.serial.close()  # Close serial
            time.sleep(0.01)     # Wait a moment
            del self.serial      # Deconstruct serial Object

        # 3. refresh last reset time
        self.last_reset_time = time.time()
        self.last_exception = ""

        # 4. re open Serial
        try:
            self.serial = serial.Serial(self.port, self.baud, timeout =0, write_timeout=0.1)
        except Exception as E:
            self.last_exception = repr(E)
            return -1

    """
    C. Public Functions
    """
    # [C.1] write "data" to serial port
    def write(self,data):
        # 1. try to send
        try :
            self.serial.write(str(data).encode())
        # 2. Fail to send data
        except Exception as E :
            self.last_exception = repr(E)
            self.reset()
            return -1
        # 3. Success to send data
        else :
            return 0

    # [C.2] read msgs form serial port , if exist.
    def read(self):
        # Reference :
        # https://stackoverflow.com/questions/17553543/pyserial-non-blocking-read-loop
        try:
            if self.serial.inWaiting()> 0:
                self.received_msg = ""
            # 1. if received some data
            while self.serial.inWaiting() > 0:
            # 1.1 try to read receive data
                data_str = self.serial.read(self.serial.inWaiting()).decode('ascii')
                self.received_msg += data_str
        # 1.2 Fail to read
        except SerialException :
            self.last_exception = "PINO_UART.read(), SerialException"
            self.reset()
            return -1
        except Exception as E:
            self.last_exception =  "PINO_UART.read()"+ repr(E)
            self.reset()
            return -1
        # 1.3 Success to read
        else :
            return 0

"""
Module TEST codes 
"""
def test():
    uart = Pino_UART()
    uart.write("asdf")
    uart.read()
    print("R:",uart.received_msg)

if __name__ == '__main__':
    test()