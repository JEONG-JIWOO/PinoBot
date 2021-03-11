import board
from modules.Hardware.I2C.pino_oled import Pino_OLED
import socket

if __name__ == "__main__":
    I2C_BUS = board.I2C()
    oled = Pino_OLED(I2C_BUS, "/home/pi/Desktop/PinoBot/")
    hostname = socket.gethostname()
    oled.send_text(hostname + '/')