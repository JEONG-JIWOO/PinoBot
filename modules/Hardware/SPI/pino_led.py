#!/usr/bin/python3

import spidev, time


class Pino_LED:
    def __init__(self, on=True):
        # 0. arguments
        self.on = on
        # 1. Static Variables

        # 2. variables
        self.last_reset_time = 0
        self.last_exception = ""

    def write(self, rgb_s, b_persent=100):
        # 1. check global self.on variable
        if not self.on:
            return 0


        # 2. calculate power and brightness
        power = int(b_persent * 31 / 100.0)
        ledstart = (power & 31) | 224
        leds = [0b11100000, 0, 0, 0] * 2

        # 3. set start bytes
        leds[0] = ledstart
        leds[4] = ledstart

        # 4. filter and set rgb value.
        # if input list < 0 -> turn off all led.
        # if input list > 6 -> ignore over 6th value
        for index in range(len(rgb_s)):
            if index == 0:
                leds[3] = rgb_s[index]
                leds[7] = rgb_s[index]
            elif index == 1:
                leds[2] = rgb_s[index]
                leds[6] = rgb_s[index]
            elif index == 2:
                leds[1] = rgb_s[index]
                leds[5] = rgb_s[index]

            elif index == 3:
                leds[7] = rgb_s[index]
            elif index == 4:
                leds[6] = rgb_s[index]
            elif index == 5:
                leds[5] = rgb_s[index]

        # 5. start spi comm
        spi = spidev.SpiDev()  # Init the SPI device
        spi.open(0, 1)
        spi.xfer2([0] * 4)
        spi.xfer2(leds)
        spi.xfer2([0xFF] * 4)
        spi.close()  # free spi device
        return 0
