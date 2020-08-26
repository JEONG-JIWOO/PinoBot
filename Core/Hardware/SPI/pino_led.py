import spidev , time

class Pino_LED:
    def __init__(self,on = True):
        # 0. arguments

        self.on = on
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
        pass

    def reset(self):
        # 1. check last reset time,
        #    only can reset after 1min after last reset
        if (time.time() - self.last_reset_time) < 60:
            return 0

        # 2. if spi, and cs exists..

        # 3. refresh last reset time
        self.last_reset_time = time.time()
        self.last_exception = ""

        # 4. re-open cs,spi and turn-off led
        try:
            self.write([0,0,0,0,0,0])

        except Exception as E:
            self.last_exception = "RGB_LED.reset()" + repr(E)
            return -1

    def write(self,rgb_s,b_persent=100):
        if not self.on:
            return 0

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

            # 4. start spi comm
            spi = spidev.SpiDev()  # Init the SPI device
            spi.open(0, 1)
            spi.xfer2([0] * 4)
            spi.xfer2(leds)
            spi.xfer2([0xFF] * 4)
            spi.close()            # free spi device

        # 2. Fail to send data
        except Exception as E :
            self.last_exception = "RGB_LED.write(" + str(rgb_s) +","+str(b_persent) + "), " + repr(E)
            self.reset()
            return -1
        # 3. Success to send data
        else :
            return 0


