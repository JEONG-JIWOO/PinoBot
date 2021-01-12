"""
Module TEST codes

Core.Hardware.SPI.Pino_LED
"""

import unittest


def custom_function():
    """
    Module TEST codes
    """
    # 1. init test
    from modules.Hardware.v1 import HardwareV1
    import configparser

    config = configparser.ConfigParser()
    with open("/home/pi/Desktop/PinoBot/config.ini") as fp:
        config.read_file(fp)

    hardware = HardwareV1(config=config, base_path="/home/pi/Desktop/PinoBot/")

    hardware.write(
        text="앞으로", led=[0, 0, 100], servo_angle=[45, 45, 90, 29, 60], servo_time=2
    )
    hardware.write(
        text="아래로",
        led=[0, 100, 100],
        servo_angle=[135, 135, 90, 180, 180],
        servo_time=2,
    )
    hardware.write(
        text="위로", led=[255, 255, 255], servo_angle=[0, 0, 0, 10, 10], servo_time=2
    )
    hardware.write(
        text="다시 기본", led=[0, 0, 50], servo_angle=[30, 30, 80, 26, 30], servo_time=2
    )
    hardware.SERVO.set_default()

    # 2. function test
    # valid case
    print("=====valid!=====")
    hardware.write(text="하이루", led=[0, 0, 100], servo_angle=[0, 0, 90], servo_time=2)
    hardware.write(image="test.jpg")
    hardware.write(text="아아")
    hardware.write(serial_msg="test_msg_logs")
    print(hardware.read())

    run_pyaudio()
    print("=====Invalid!=====")
    # invalid case
    hardware.write(text=1)
    hardware.write(led=1)
    hardware.write(servo_angle=1)
    hardware.write(serial_msg=1)
    print(hardware.read())

    # 3. reset test
    hardware.reset()

    # 4. function test after reset
    print("=====valid!=====")
    hardware.write(text="하이루", led=[0, 0, 100], servo_angle=[0, 0, 120], servo_time=2)
    hardware.write(image="test.jpg")
    hardware.write(text="아아")
    hardware.write(serial_msg="test_msg_logs")
    hardware.write(
        text="기본값 설정", led=[0, 0, 100], servo_angle=[30, 30, 80, 30, 30], servo_time=2
    )
    print(hardware.read())

    run_pyaudio()
    print("=====Invalid!=====")
    # invalid case
    hardware.write(text=1)
    hardware.write(led=1)
    hardware.write(servo_angle=1)
    hardware.write(serial_msg=1)
    print(hardware.read())

    # 5. del test
    del hardware


def run_pyaudio():
    import pyaudio
    import wave

    audio = pyaudio.PyAudio()
    stream = audio.open(
        format=pyaudio.paInt16,
        channels=2,
        rate=16000,
        input=True,
        frames_per_buffer=2048,
        input_device_index=2,
    )

    a = stream.read(2048, exception_on_overflow=False)
    print(a)
    stream.close()


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


if __name__ == "__main__":
    unittest.main()
