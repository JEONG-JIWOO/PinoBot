"""
Module TEST codes

Core.Hardware.SPI.Pino_LED
"""

import unittest
import tracemalloc
import psutil
import os


def event_test():
    tracemalloc.start()
    from pinobot import PinoBot

    # 1. test talk
    bot = PinoBot()
    cnt = 0
    snap = tracemalloc.take_snapshot()
    snap_0 = snap
    while True:
        # Do try , Except on in here
        try:
            cnt += 1
            bot.main_loop_once()

            if cnt % 3 == 0:
                """
                snap_new = tracemalloc.take_snapshot()
                print("Compare TOP 5 with start")
                for stat in snap_0.compare_to(snap_new, "lineno")[:5]:
                    print("%03.2f KB    + %03.2f KB"%(stat.size/1000,stat.size_diff/1000))

                print("=" * 30)
                print("Compare TOP 5 with before loop")
                for stat in snap_0.compare_to(snap_new, "lineno")[:5]:
                    print("%03.2f KB   + %03.2f KB"%(stat.size/1000,stat.size_diff/1000))

                snap = snap_new
                """
                pid = os.getpid()
                current_process = psutil.Process(pid)
                current_process_memory_usage_as_KB = (
                    current_process.memory_info()[0] / 2.0 ** 20
                )
                print(
                    f" Current memory KB   : {current_process_memory_usage_as_KB: 9.3f} KB"
                )

        except Exception as E:
            bot.log.error(repr(E))


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
