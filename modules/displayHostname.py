import board
from Hardware.I2C.pino_oled import Pino_OLED
import socket
import time

if __name__ == "__main__":
    # OLED setup
    I2C_BUS = board.I2C()
    oled = Pino_OLED(I2C_BUS, "/home/pi/Desktop/PinoBot/")

    for i in range(5):
        # Check internet
        try:
            oled.send_text("Checking\ninternet"+i*".")
            time.sleep(0.5)
            from urllib3 import PoolManager, Timeout, Retry

            http = PoolManager(
                timeout=Timeout(connect=3.0, read=2.0), retries=Retry(2, redirect=0)
            )
            response = http.request("HEAD", "https://status.cloud.google.com/")

        # Failed
        except Exception as E:
            time.sleep(3)
            # retry

        # Success
        else:
            hostname = socket.gethostname()

            s2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s2.connect(("8.8.8.8", 0))
            ip_addr = s2.getsockname()[0]

            print('hostname:', hostname)
            print("ip address:", ip_addr)
            oled.send_text(f'{ip_addr}\n{hostname}')
            exit(0)

    # Failed many times to connect url
    oled.send_text('Internet\nerror')