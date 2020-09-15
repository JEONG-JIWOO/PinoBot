"""
Module TEST codes

Core.Hardware.SPI.Pino_LED
"""

import unittest

def custom_function():

    # 1. init test
    from Core.Hardware.SPI import pino_led
    import time
    led = pino_led.Pino_LED()

    # 2. working test
    time.sleep(1)
    led.write([100])
    time.sleep(1)
    led.write([100,100])
    time.sleep(1)
    led.write([100,100,100])
    time.sleep(1)
    led.write([100,100,100,100])
    time.sleep(1)
    led.write([100,100,100,100,100])
    time.sleep(1)
    led.write([100,100,100,100,100,100])
    print("E:", led.last_exception)

    # 3. reset test
    led.reset()

    # 4. working after reset test
    time.sleep(1)
    led.write([100])
    time.sleep(1)
    led.write([100,100])
    time.sleep(1)
    led.write([100,100,100])
    time.sleep(1)
    led.write([100,100,100,100])
    time.sleep(1)
    led.write([100,100,100,100,100])
    time.sleep(1)
    led.write([100,100,100,100,100,100])
    print("E:", led.last_exception)

    # del test
    del led

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



