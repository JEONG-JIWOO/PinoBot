import time
import busio
import board
import digitalio
from adafruit_bus_device.spi_device import SPIDevice

class RGB_LED():
    def __init__(self,spi):
        # 0. arguments
        self.spi = spi

        # 1. Static Variables

        # 2. variables
        self.last_reset_time = 0
        self.last_exception = ""

        # 3. Objects
        self.cs = None
        self.spi_bus = None

        # 4. Init Functions
        self.reset()

    def __del__(self):
        if self.spi_bus is not None:
            try:
                del self.spi_bus
            except:
                pass
        if self.cs is not None:
            try:
                del self.cs
            except:
                pass

    def reset(self):
        # 1. check last reset time,
        #    only can reset after 1min after last reset
        if (time.time() - self.last_reset_time) < 60:
            return 0

        # 2. if spi, and cs exists..
        if self.spi_bus is not None:
            del self.spi_bus
        if self.cs is not None:
            del self.cs

        # 3. refresh last reset time
        self.last_reset_time = time.time()
        # 4. re-open cs,spi and turn-off led
        try:
            self.cs = digitalio.DigitalInOut(board.D18)
            self.spi_bus  = SPIDevice(self.spi, self.cs)
            self.write([0,0,0,0,0,0])

        except Exception as E:
            self.last_exception = "RGB_LED.reset()" + repr(E)
            return -1

    def write(self,rgb_s,b_persent=100):
        try :
            # 1. calculate power and brightness
            power = int(b_persent * 31 / 100.0)
            ledstart = (power & 31) | 224
            leds = [0b11100000, 0, 0, 0] * 2

            # 2. set start bytes
            leds[0] = ledstart
            leds[4] = ledstart

            # 3. filter and set rgb value.
            # if input list < 0 -> turn off all led.
            # if input list > 6 -> ignore over 6th value
            for index in range(len(rgb_s)):
                if index == 0:
                    leds[3] = rgb_s[index]
                elif index == 1:
                    leds[2] = rgb_s[index]
                elif index == 2:
                    leds[1] = rgb_s[index]

                elif index == 3:
                    leds[7] = rgb_s[index]
                elif index == 4:
                    leds[6] = rgb_s[index]
                elif index == 5:
                    leds[5] = rgb_s[index]

            # 4. start spi commm
            with self.spi_bus as bus_device:
                bus_device.write(bytes([0] * 4))    # FIRST 4byte is Empty.
                bus_device.write(bytes(leds))       # Send DATA
                bus_device.write(bytes([0xFF] * 4)) # LAst 4byte

        # 2. Fail to send data
        except Exception as E :
            self.last_exception = "RGB_LED.write(" + str(rgb_s) +","+str(b_persent) + "), " + repr(E)
            self.reset()
            return -1
        # 3. Success to send data
        else :
            return 0


def test():
    comm_port = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
    D = RGB_LED(comm_port)
    time.sleep(1)
    D.write([0,0,100,0,100])
    time.sleep(1)
    D.write([100,0,0,100])
    time.sleep(1)
    D.write([0,50])
    print("E:" , D.last_exception)

if __name__ == '__main__':
    test()



"""
    import spidev
    spi = spidev.SpiDev()  # Init the SPI device
    spi.open(0,1)
    set_pixel(spi, [0, 200, 0])
    spi.xfer2([0] * 4)
    spi.xfer2(leds)
    spi.xfer2([0xFF] * 4)
"""