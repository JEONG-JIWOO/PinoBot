import board
from modules.Hardware.I2C.pino_oled import Pino_OLED
import socket , time
from subprocess import check_output

if __name__ == "__main__":

    I2C_BUS = board.I2C()
    oled = Pino_OLED(I2C_BUS, "/home/pi/Desktop/PinoBot/")

    connected = False
    for i in range(5):
        try:
            oled.send_text("internet \n check"+i*".")
            time.sleep(0.5)
            from urllib3 import PoolManager, Timeout, Retry

            http = PoolManager(
                timeout=Timeout(connect=3.0, read=2.0), retries=Retry(2, redirect=0)
            )
            response = http.request("HEAD", "https://status.cloud.google.com/")

        except Exception as E:
            time.sleep(3)
            oled.send_text("internet \n wait."+i*".")

        else :
            hostname = socket.gethostname()
            ip = check_output(['hostname', '-I']).decode().strip()
            print("internet on \nhostname :", hostname)
            print("ip :", hostname)
            oled.send_text(ip + "\n " + hostname)
            connected = True
            break

    if not connected :
        oled.send_text("internet \n error "+i*".")