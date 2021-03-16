import unittest
from modules.Hardware.pino_uart import Pino_UART
import time

class MyTestCase(unittest.TestCase):
    def test_something(self):
        from modules.Hardware.pino_uart import Pino_UART
        print('start')
        uart = Pino_UART()
        uart.write("ready")
        time.sleep(3)


if __name__ == '__main__':
    unittest.main()
