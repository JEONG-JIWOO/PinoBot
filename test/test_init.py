"""
Module TEST codes

Core.Hardware.SPI.Pino_LED
"""

import unittest


def custom_function():
    from modules.pino_init import Pino_Init

    d = Pino_Init("~/Desktop/Desktop/PinoBot/")
    d.boot()
    print("tested")

    del d


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
