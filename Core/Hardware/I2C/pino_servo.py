#!/usr/bin/python3


import time
# Adafruit Libraries
# https://github.com/adafruit/Adafruit_CircuitPython_PCA9685
# https://github.com/adafruit/Adafruit_CircuitPython_Motor

# Import the PCA9685 module.
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo

class Pino_SERVO:
    """
    A. con & deconstruct
    """
    def __init__(self, i2c, num_motor = 8,
                 motor_enable = (1, 1, 1, 1, 1, 1, 1, 1),
                 motor_min_angle = (0, 0, 0, 0, 0, 0, 0, 0),
                 motor_max_angle = (170, 170, 170, 170, 170, 170, 170, 170),
                 motor_default_angle =(0, 0, 0, 0, 0, 0, 0, 0)):

        # 0. arguments
        self.i2c = i2c
        self.num_motor = num_motor
        self.motor_enable = list(motor_enable)
        self.max_angle_limit = list(motor_max_angle)
        self.min_angle_limit = list(motor_min_angle)
        self.motor_default_angle = list(motor_default_angle)

        # 1. Static Variables
        self.pwm_min = 580 # min pwm, sg-90 : -90,
        self.pwm_max = 2480 # max pwm, sg-90 : +90,
        self.min_trj_time = 0.3
        self.max_trj_time = 15
        self.control_time = 0.02

        # 2. variables
        self.servos = []
        self.cur_angles = [0,0,0,0,0,0,0,0]
        self.last_reset_time = 0
        self.last_exception = ""
        self.force_stop_flag = False

        # 3. Objects
        self.pca = None

        # 4. Init Functions
        self.reset()

    def __del__(self):
        # noinspection PyBroadException
        try:
            self.pca.deinit()
            del self.pca
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

        # 2. if self.pca exists..
        if self.pca is not None:
            self.pca.deinit()
            del self.pca

        # 3. refresh last reset time
        self.last_reset_time = time.time()
        self.last_exception = ""

        # 4. re open Serial
        try:
            self.pca = PCA9685(self.i2c)
            self.pca.frequency = 50
            self.servos = []
            for i in range(8):
                self.servos.append(servo.Servo(self.pca.channels[i], min_pulse=self.pwm_min, max_pulse=self.pwm_max))
        except Exception as E:
            self.last_exception = "SERVO.reset()" + repr(E)
            return -1

    """
    C. Public Functions
    """
    # [C.1] make trajectory and send to servo
    # TODO : Make this as Multi-threading Function, but should make stop
    def write(self,tar_angles,trj_time):
        # 1. check tar_angle is Valid
        #    1-1 len(tar_angles) == self.num_motor : VALID, pass
        #    1-2 len(tar_angles) <  self.num)motor : VALID, pass
        #    1-3 len(tar_angles) >  self.num)motor : INVALID
        if len(tar_angles) > self.num_motor :
            del tar_angles[self.num_motor:]  # cut out-ranged value.
        elif len(tar_angles) == 0 :
            return 0

        try:
            # 2. check trj_time is Valid
            if trj_time < self.min_trj_time:
                trj_time = self.min_trj_time
            elif trj_time > self.max_trj_time:
                trj_time = self.max_trj_time

            # 3. get actuate_motor_index_list
            actuate_motor_index_list =[]
            for index in range(len(tar_angles)):
                if self.motor_enable[index] == 1:
                    actuate_motor_index_list.append(index)
            # ex)  actuate_motor_index_list -> [0,1,2,3,4]  or like..[0,1,2,4,6]

            # 4. start to make trajectory
            trjs = []
            for index in actuate_motor_index_list:
                # 4-1 if motor is enabled, check target angle is Valid
                tar_angle = tar_angles[index]
                if tar_angle < self.min_angle_limit[index]:
                    tar_angle = self.min_angle_limit[index]
                elif tar_angle > self.max_angle_limit[index]:
                    tar_angle = self.max_angle_limit[index]
                # 4-2 calculate trajectory
                trjs.append(self._make_trj(self.cur_angles[index],tar_angle,trj_time))

            # 5. init trajectory
            """
             self.num_motor = 5
             run_motor_n = [0,1,2,3,4]
             trjs : [
             [5,10,15,20,25,30,35,40]
             [1, 2, 3, 4, 5, 6, 7, 8]
             [5,10,15,20,25,30,35,40]
             [1, 2, 3, 4, 5, 6, 7, 8]
             [1, 2, 3, 4, 5, 6, 7, 8]
             ]
            """
            # 5.1 run trajectory
            for j in range(len(trjs[0])):
                # 4.2 start 50ms cycle
                start_time = time.time()
                for motor_n in range(len(actuate_motor_index_list)):
                    new_angle =  trjs[motor_n][j]
                    if self.cur_angles[motor_n] != new_angle:  # if motor angle is same as before, skip i2c comm
                        self.servos[motor_n].angle = new_angle
                        self.cur_angles[motor_n] = new_angle
                # 5.3 calculate wait time
                wait_time = self.control_time - (time.time() - start_time)
                time.sleep(wait_time) # sleep for few milliseconds, and makes all loop done, in exactly 20ms

                # 5.4 check if force stop initiated,
                if self.force_stop_flag:
                    return 0

            # 6. last fit to target angle
            for index in range(len(actuate_motor_index_list)):
                self.servos[index].angle = tar_angles[index]

        except Exception as E:
            self.last_exception = "SERVO.write("+str(tar_angles)+","+str(trj_time)+"), "+repr(E)
            print(self.last_exception)
            return -1
        else:
            return 0

    def set_default(self):
        self.write(self.motor_default_angle,1)
    """
    D. Private Functions
    """
    # [D.1] Draw Trajectory
    def _make_trj(self,cur_angle,tar_angle,trj_time):
        # linear trajectory
        # TODO : F-curve trajectory
        n_steps = int(trj_time/self.control_time)
        trj = []
        for i in range(n_steps):
            trj.append(cur_angle + int( i*(tar_angle - cur_angle)/n_steps))
        return trj

