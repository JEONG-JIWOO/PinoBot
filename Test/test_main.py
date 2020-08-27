"""
Module TEST codes

Core.Hardware.SPI.Pino_LED
"""

import unittest


def event_test():
    from Core.pino_main import PinoBot
    a = PinoBot()

    # 5. fail handler False
    a.run_task(["event", "Fail_NoMatch_Intents", None, False])

    # 1. valid
    a.run_task(["event","Fail_NoMatch_Intent",None,True]) #  FailNoMatchIntent

    p = {'a':'asdf'}
    # 2. add not needed parameter
    a.run_task(["event", "Fail_NoMatch_Intent",p, True])  #  FailNoMatchIntent

    # 3. invalid event name
    a.run_task(["event", "Fail_NoMatch_Intents",None, True]) # FailNoMatchIntent

    # 4. invalid event name & parameter
    a.run_task(["event", "Fail_NoMatch_Intents",p, True]) # FailNoMatchIntent

    # 5. fail handler False
    a.run_task(["event", "Fail_NoMatch_Intents", None, False])


class CustomTests(unittest.TestCase):
    def setUp(self):
        """ 테스트 시작전 테스트 설정"""
        pass

    def tearDown(self):
        """ 테스트 끝난이후 실행되는 함수"""
        pass

    def test_runs(self):
        """ 실 테스트 코드 """
        event_test()

if __name__ == '__main__':
    unittest.main()

def custom_function():
    from Core.pino_main import PinoBot
    d = PinoBot()
    d.run()

