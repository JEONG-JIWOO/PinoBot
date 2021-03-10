from modules import pinobot
import socket

if __name__ == "__main__":
    bot  = pinobot.PinoBot()
    hostname = socket.gethostname()
    bot.hardware.write(text=f'{hostname}/')