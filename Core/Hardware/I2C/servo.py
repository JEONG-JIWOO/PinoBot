from __future__ import division
import time
import Adafruit_PCA9685

class SERVO():
    def __init__(self):
        # 1. Static Variables
        self.pwm_min = 100 # min pwm, sg-90 : -90,
        self.pwm_max = 550 # max pwm, sg-90 : +90,
        self.rate = (self.pwm_max-self.pwm_min)/180  # rate, for angle -> pwm transformation

        # 2. variables
        # set safety limit
        # motor index [  0,  1,  2,  3,  4,  5,  6,  7
        #                8,  9, 10, 11, 12, 13, 14, 15]

        self.max_angle_limit = [180,180, 120,  0,  0,  0,  0,  0,
                                0  ,  0,   0,  0,  0,  0,  0,  0]

        self.min_angle_limit = [  0,  0,  0,  0,  0,  0,  0,  0,
                                  0,  0,  0,  0,  0,  0,  0,  0]

        # 3. Objects
        self.board = None

        # 4. Init Functions
        self.reset()

    def __del__(self):
        del self.board

    def reset(self):
        # 1. check last reset time,
        #    only can reset after 1min after last reset
        if (time.time() - self.last_reset_time) < 60:
            return 0

        # 2. if self.serial exists..
        if self.board is not None:
            del self.board
            self.board = Adafruit_PCA9685.PCA9685()

        # 3. refresh last reset time
        self.last_reset_time = time.time()

        # 4. re open Serial
        try:
            self.board.set_pwm_freq(50)  # 50Hz = 20ms
        except Exception as E:
            self.last_exception = str(E)
            return -1

    def write(self,data):
        pass

    def send_angles(self,index,angle):
        # angle : 0~180

        # 1. check index is valid
        if index <0 or index > 16 :
            return 0

        # 2. check safety limit
        elif angle < self.min_angle_limit[index]:
            angle = self.min_angle_limit[index]

        elif angle > self.max_angle_limit[index]:
            angle = self.max_angle_limit[index]

        # 3. calculate new pwm value
        new_pwm = int(self.rate*angle + self.pwm_min)

        # 4. init.
        self.board.set_pwm(index,0,new_pwm)


# class test_code
def test():
    B = PCA9685()
    time.sleep(2)
    B.send_angles(8, 90)
    time.sleep(2)
    B.send_angles(8,175)
    time.sleep(2)
