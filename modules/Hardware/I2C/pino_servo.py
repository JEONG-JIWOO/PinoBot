#!/usr/bin/python3

"""
Description : PinoBot servo control module using pca9685 chip
Author : Jiwoo Jeong
Email  : Jiwoo@gepetto.io  / jjw951215@gmail.com
Reference:
    Adafruit Libraries
    https://github.com/adafruit/Adafruit_CircuitPython_PCA9685
    https://github.com/adafruit/Adafruit_CircuitPython_Motor


V 0.9  [2021-02-17]
    - still using old version
    - add comment form

v 1.0 [ WIP ]
    - [X, refactoring   ] remove hard codded code
    - [X, enhancement   ] remove reset function
    - [X, enhancement   ] remove to many try and except
    - [X, documentation ] add Comment
"""

from adafruit_pca9685 import PCA9685
from adafruit_motor import servo
import random , time


class Pino_SERVO:
    """
    A. con & deconstruct
    """

    def __init__(
        self,
        i2c,
        num_motor=8,
        motor_enable=(1, 1, 1, 1, 1, 1, 1, 1),
        motor_min_angle=(0, 0, 50, 0, 0, 0, 0, 0),
        motor_max_angle=(150, 150, 140, 60, 60, 0, 0, 0),
        motor_default_angle=(100, 100, 90, 30, 30, 0, 0, 0),
    ):

        # 0. arguments
        self.i2c = i2c
        self.num_motor = num_motor
        self.motor_enable = list(motor_enable)
        self.min_angle_limit = list(motor_min_angle)
        self.max_angle_limit = list(motor_max_angle)
        self.motor_default_angle = list(motor_default_angle)
        self.motor_direction = [-1, 1, 1, 1, -1, 0, 0, 0]

        # 1. Static Variables
        self.pwm_min = 580  # min pwm, sg-90 : -90,
        self.pwm_max = 2480  # max pwm, sg-90 : +90,
        self.min_trj_time = 0.3
        self.max_trj_time = 5
        self.control_time = 0.02

        # 2. variables
        self.servos = []
        self.cur_angles = self.motor_default_angle
        self.force_stop_flag = False
        self.sleep_mode_register = None
        self.operation_mode_register = 33

        # 3. Objects

        # 4. Init Functions
        self.pca = PCA9685(self.i2c)
        self.sleep_mode_register = (self.operation_mode_register & 0x7F) | 0x10
        self.pca.frequency = 50
        self.servos = []
        for i in range(8):
            self.servos.append(
                servo.Servo(
                    self.pca.channels[i],
                    min_pulse=self.pwm_min,
                    max_pulse=self.pwm_max,
                )
            )
        self.sleep()

    def sleep(self):  # set pca9685 to sleep mode
        self.pca.mode1_reg = self.sleep_mode_register
        return 0

    def wake_up(self):  # set pca9685 to opteration mode
        self.pca.mode1_reg = self.operation_mode_register
        return 0

    """
    C. Public Functions
    """
    # [C.1] make trajectory and send to servo
    # TODO : Make this as Multi-threading Function, but should make stop
    def write(self, tar_angles, trj_time):
        #print(tar_angles,trj_time)
        # 1. check tar_angle is Valid
        #    1-1 len(tar_angles) == self.num_motor : VALID, pass
        #    1-2 len(tar_angles) <  self.num)motor : VALID, pass
        #    1-3 len(tar_angles) >  self.num)motor : INVALID
        if len(tar_angles) > self.num_motor:
            del tar_angles[self.num_motor :]  # cut out-ranged value.
        elif len(tar_angles) == 0:
            return 0

        self.wake_up()

        # 2. check trj_time is Valid
        if trj_time < self.min_trj_time:
            trj_time = self.min_trj_time
        elif trj_time > self.max_trj_time:
            trj_time = self.max_trj_time

        # 3. get actuate_motor_index_list
        actuate_motor_index_list = []
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
            if tar_angle > self.max_angle_limit[index]:
                tar_angle = self.max_angle_limit[index]
            # 4-2 calculate trajectory
            trjs.append(self._make_trj(self.cur_angles[index], tar_angle, trj_time))

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
                new_angle = trjs[motor_n][j]
                if (
                    self.cur_angles[motor_n] != new_angle
                ):  # if motor angle is same as before, skip i2c comm
                    if self.motor_direction[motor_n] == 1:
                        self.servos[motor_n].angle = int(new_angle)
                        self.cur_angles[motor_n] = new_angle
                    elif self.motor_direction[motor_n] == -1:
                        self.servos[motor_n].angle = int( 180 - new_angle)
                        self.cur_angles[motor_n] = new_angle
            # 5.3 calculate wait time
            wait_time = self.control_time - (time.time() - start_time)
            if wait_time > 0:
                # sleep for few milliseconds,
                # and makes all loop done, in exactly 20ms
                time.sleep(wait_time)

            # 5.4 check if force stop initiated,
            if self.force_stop_flag:
                self.sleep()
                return 0

        self.sleep()
        return 0


    def set_default(self):
        self.write(self.min_angle_limit, 1 )
        self.write(self.max_angle_limit, 1 )
        self.write(self.min_angle_limit, 1 )
        self.write(self.max_angle_limit, 1 )
        self.write(self.motor_default_angle, 1)
        return 0

    def cal_random_motion(self, t):
        motion = [t]
        for i in range(self.num_motor):
            if i == 0 or 1:
                motion.append(
                    random.randint(75 - 50, 75 + 50)
                )  # [TODO], Change Hard Cording
            elif i == 2:
                motion.append(random.randint(80 - 30, 80 + 30))
            elif i == 3 or 4:
                motion.append(random.randint(15 - 12, 15 + 5))
        return motion

    """
    D. Private Functions
    """
    # [D.1] Draw Trajectory
    def _make_trj(self, cur_angle, tar_angle, trj_time):
        # linear trajectory
        # TODO : F-curve trajectory
        n_steps = int(trj_time / self.control_time)
        trj = []
        for i in range(n_steps):
            trj.append(cur_angle + int(i * (tar_angle - cur_angle) / n_steps))
        return trj
