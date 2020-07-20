import RPi.GPIO
import time

"""
Reference
https://m.blog.naver.com/PostView.nhn?blogId=chandong83&logNo=221155355360

"""


# noinspection PyPep8Naming
class Pino_GPIO:
    """
    A. con & deconstruct
    """
    def __init__(self):
        # 1. Static Variables
        self.MAX_DISTANCE = 150  # [cm] Max Boundary distance
        self.TIMEOUT = self.MAX_DISTANCE* 2 * 29.41  # [ms] sensor timeout limits
        self.SW_Pin = 17    # [GPIO17] Volume switch pin
        self.TRIG_Pin = 23  # [GPIO23] sonic sensor trigger pin
        self.ECHO_Pin = 24  # [GPIO24] sonic sensor echo pin

        # 2. variables
        self.distance = 0   # [cm] Measured distance
        self.sw_flag = False
        self.volume = 0     # 0 ~ 9 relative Speaker Volume
        self.last_reset_time = 0
        self.last_exception = ""

        # 3. Objects
        self.GPIO = None

        # 4. Init Functions
        self.reset()

    def __del__(self):
        # Free GPIO
        self.GPIO.setmode(self.GPIO.BCM)
        self.GPIO.cleanup((self.TRIG_Pin,self.ECHO_Pin))
        # noinspection PyBroadException
        try:
            del self.GPIO
        except :
            pass
    """
    B. reset 
    """
    def reset(self):
        # 1. check last reset time,
        #    only can reset after 1min after last reset
        if (time.time() - self.last_reset_time) < 60:
            return 0

        # 2. if self.GPIO exists..
        if self.GPIO is not None:
            self.GPIO.cleanup()  # Close gpio
            time.sleep(0.01)     # Wait a moment
            del self.GPIO      # Deconstruct gpio Object

        # 3. refresh last reset time
        self.last_reset_time = time.time()

        # 4. re open GPIO
        try:
            # 4.1 init GPIO
            self.GPIO = RPi.GPIO
            self.GPIO.setmode(self.GPIO.BCM)
            # 4.2 init GPIO PINS
            self.GPIO.setup(self.SW_Pin  , self.GPIO.IN , pull_up_down=self.GPIO.PUD_DOWN)
            self.GPIO.setup(self.TRIG_Pin, self.GPIO.OUT)

            self.GPIO.setup(self.ECHO_Pin, self.GPIO.IN , pull_up_down=self.GPIO.PUD_DOWN)
            # 4.3 init GPIO interrupt
            self.GPIO.add_event_detect(self.SW_Pin, self.GPIO.RISING, callback=self.__sw_callback,)

        except Exception as E:
            self.last_exception = "reset() ," +repr(E)
            return -1

    """
    C. Public Functions
    """
    # [C.1] read ultra sonic sensor, and store at "self.distance"
    def read_sonic_sensor(self):
        try :
            # 1. send start signal to Trigger pin
            self.GPIO.output(self.TRIG_Pin, True)
            time.sleep(0.00001)
            self.GPIO.output(self.TRIG_Pin, False)

            # 2. receive response
            measure_start: float = time.time()
            pulse_start = 0
            pulse_end = 0

            # 3. wait for first pulse.
            while self.GPIO.input(self.ECHO_Pin) == 0:
                pulse_start = time.time()
                if ((pulse_start - measure_start)*1000000) >= self.TIMEOUT :
                    return 150

            # 4. measure time for last pulse.
            # measure_start = time.time()
            while self.GPIO.input(self.ECHO_Pin) == 1:
                pulse_end = time.time()
                if ((pulse_end - pulse_start)*1000000) >=  self.TIMEOUT:
                    return 150

            # 5. change time to distance
            self.distance = ( (pulse_end - pulse_start) * 17001) # 1000000/2 / 29.41

        except Exception as E:  # if Error occurs
            self.last_exception = "read_sonic_sensor() ," +repr(E)  # save error Message
            print(self.last_exception)
            self.reset()  # reset gpio
            return -1

        else :
            return self.distance

    """
    D. Private Functions
    """
    # [D.1] switch interrupt callback
    def __sw_callback(self,channel):
        # change sw_flag to True
        if not self.sw_flag:
            self.sw_flag = True
            # Volume Switch Interrupt Function
            # Volume changes circular 0 -> 1 -> 2 ..... -> 9 -> 0
            if self.volume > 9:
                self.volume = 0
            else :
                self.volume +=1

"""
Module TEST codes 
"""
def test():
    sensor = Pino_GPIO()
    while 1:
        time.sleep(0.1)
        distance = sensor.read_sonic_sensor()
        if distance > 0:
            print(distance)
        if sensor.sw_flag :
            print(sensor.volume)
            sensor.sw_flag = False

if __name__ == '__main__':
    test()
