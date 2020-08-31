"""
Module TEST codes

Core.Hardware.SPI.Pino_LED
"""

import unittest

def custom_function():
    """
    Module TEST codes
    """
    from Core.Hardware.v1 import HardwareV1
    import configparser
    config = configparser.ConfigParser()
    config.read_file(open("/home/pi/Desktop/PinoBot/config.ini"))

    hardware = HardwareV1(config=config, base_path="/home/pi/Desktop/PinoBot/")

    # valid case
    print("=====valid!=====")
    hardware.write(text="하이루", led=[0, 0, 100], servo_angle=[180, 180, 90], servo_time=2)
    hardware.write(image="test.jpg")
    hardware.write(text="아아")
    hardware.write(serial_msg="test_msg_logs")
    print(hardware.read())

    print("=====Invalid!=====")
    # invalid case
    hardware.write(text=1)
    hardware.write(led=1)
    hardware.write(servo_angle=1)
    hardware.write(serial_msg=1)
    print(hardware.read())
    del hardware

class CustomTests(unittest.TestCase):
    def setUp(self):
        """ 테스트 시작전 테스트 설정"""
        pass

    def tearDown(self):
        """ 테스트 끝난이후 실행되는 함수"""
        pass

    def test_runs(self):
        """ 실 테스트 코드 """
        custom_function()

if __name__ == '__main__':
    unittest.main()



