"""
Module TEST codes

Core.Hardware.SPI.Pino_LED
"""

import unittest


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

def custom_function():
    from Core.pino_main import PinoBot
    d = PinoBot()
    d.run()

