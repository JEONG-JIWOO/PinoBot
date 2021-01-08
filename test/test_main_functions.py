"""
Module TEST codes

Core.Hardware.SPI.Pino_LED
"""

import unittest
import tracemalloc


def event_test():
    tracemalloc.start()
    from pino_main import PinoBot

    a = PinoBot()

    mem1 = tracemalloc.take_snapshot()
    display_mem(mem1)

    # 1. test talk
    print("\n\n#1. talk\n")

    a.add_task("talk")
    a.main_loop_once()

    # 2. test basic event
    print("\n\n#2. basic event\n")

    p = {"a": "asdf"}  # parameter that not used, for these events, but add for test

    a.add_task("event", "WakeUp_Event", None, True)
    a.main_loop_once()

    a.add_task("event", "Sleep_Event", None, True)
    a.main_loop_once()

    a.add_task("event", "SleepEnter_Event ", p, True)
    a.main_loop_once()

    a.add_task("event", "Wait_Event", None, True)
    a.main_loop_once()

    a.add_task("event", "FailNotTalk_Intent", p, True)
    a.main_loop_once()

    a.add_task("event", "FailNoMatch_Intent", None, True)
    a.main_loop_once()

    display_mem(mem1)

    # 3. test invalid event name
    print("\n\n#3. invalid event name\n")

    # invalid name, but handler false -> nothing
    a.add_task("event", "FailNoMatch_Intents", None, False)
    a.main_loop_once()

    # invalid name, but handler True -> FailNoMatch_Intents
    a.add_task("event", "Fail", None, True)
    a.main_loop_once()

    # 4. invalid dialogflow action test
    a.add_task("event", "invalidAction", None, True)
    a.main_loop_once()

    display_mem(mem1)

    del a

    display_mem(mem1)

    a = PinoBot()
    display_mem(mem1)

    a.add_task("event", "FailNoMatch_Intents", None, False)
    a.main_loop_once()

    display_mem(mem1)


def display_mem(mem_b):
    mem3 = tracemalloc.take_snapshot()
    for stat in mem3.compare_to(mem_b, "lineno")[:10]:
        print(stat)


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


if __name__ == "__main__":
    unittest.main()
