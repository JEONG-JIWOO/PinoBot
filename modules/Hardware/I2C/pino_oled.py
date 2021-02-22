#!/usr/bin/python3

"""
Description : PinoBot I2C oled control module
Author : Jiwoo Jeong
Email  : Jiwoo@gepetto.io  / jjw951215@gmail.com
Reference:
    pip3 install adafruit-circuitpython-ssd1306
    https://github.com/adafruit/Adafruit_CircuitPython_SSD1306


V 0.9  [2021-02-17]
    - still using old version
    - add comment form

v 1.0 [ WIP ]
    - [X, refactoring   ] remove hard codded code
    - [X, enhancement   ] remove reset function
    - [X, enhancement   ] remove to many try and except
    - [X, documentation ] add Comment
"""

from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

import time


class Pino_OLED:
    """
    Description:
    -

    Summary of Class

        1.

        2.

    """

    def __init__(self, i2c, base_path, console_font_name="", main_font_name=""):
        # 0. Argument
        self.base_path = base_path
        self.console_font_name = console_font_name
        self.main_font_name = main_font_name
        self.i2c = i2c

        # 1. Static Variables
        self.oled_size = (128, 64)
        self.main_font_size = 30
        self.console_font_size = 12

        # 2. variables
        self.console_msg = ""

        # 3. Objects
        self.main_font = None
        self.console_font = None
        self.im = None

        # 4. Init Functions
        self.oled = adafruit_ssd1306.SSD1306_I2C(
            self.oled_size[0], self.oled_size[1], self.i2c
        )
        self.oled.fill(0)
        self.oled.show()
        self.__load_font()

    def __del__(self):
        # noinspection PyBroadException
        try:
            del self.oled  # Deconstruct Object
            del self.main_font
        except:
            pass

    """
    C. Public Functions
    """
    # [C.1] find image by "image_name', from directory, and send to OLED
    def send_image(self, image_name):
        # 1. load image
        path = self.base_path + "media/image/" + image_name
        try:
            image = Image.open(path)
        except FileNotFoundError:
            self.send_text("file not found:\n image_name")
            return 0

        im = image.resize(self.oled_size)
        # 2. change to binary image and save it.
        self.im = im.convert("1")
        self.oled.image(self.im)
        self.oled.show()
        return 0

    # [C.2] convert "text" to image, and send to OLED
    # NOTE : Progress bar : NO,    text : variable size
    def send_text(self, msgs):
        image = self.__text_2_image(msgs)
        self.oled.image(image)
        self.oled.show()
        return 0

    # [C.3] show progress "step" , convert "msg" to image, and send to OLED
    # NOTE : Progress bar : YES,    text : Fixed size
    def send_loading_console(self, step, msgs, mode="a"):
        # 1. make new image by font size
        im = Image.new("L", (128, 64), 0)
        draw = ImageDraw.Draw(im)

        if mode == "a":
            self.console_msg += msgs
            # print(self.console_msg)
        else:
            self.console_msg = msgs

        # 2. draw text to image
        draw.text(
            (18, 0),
            self.console_msg,
            font=self.console_font,
            fill=255,
            spacing=2,
            align="left",
        )

        if step > 16:
            step = 16
        for i in range(step):
            self.__draw_line(draw, i)

        # 3. change to binary image and save it.
        self.im = im.convert("1")
        self.oled.image(self.im)
        self.oled.show()
        return 0


    # [C.4] show progress "step" , convert "msg" to image, and send to OLED
    # NOTE : Progress bar : YES,    text : variable size
    def send_loading_text(self, step=0, ratio=0, msg=""):
        progress_im = Image.new("L", self.oled_size, 0)
        draw = ImageDraw.Draw(progress_im)

        if step == 0:
            now_step = int(ratio * 0.16)
            for i in range(now_step):
                self.__draw_line(draw, i)

        elif step > 0:
            if step > 16:
                step = 16
            for i in range(step):
                self.__draw_line(draw, i)

        if msg != "":
            image = self.__text_2_image(msg, resize=(110, 64))
            progress_im.paste(image, (18, 0))

        self.im = progress_im.convert("1")
        self.oled.image(self.im)
        self.oled.show()
        return 0

    """
    D. Private Functions
    """
    # [D.1] load font by name, from directory
    def __load_font(self):
        # 1. try to load font from config file

        try:
            self.main_font = ImageFont.truetype(
                self.base_path + "/modules/Hardware/Fonts/" + self.main_font_name,
                self.main_font_size,
            )
            self.console_font = ImageFont.truetype(
                self.base_path + "/modules/Hardware/Fonts/" + self.console_font_name,
                self.console_font_size,
            )
        except IOError:
            print("fail to load font, load [NanumBarunGothicBold] ")
        except Exception as E:
            self.last_exception = "OLED.load_font(), No IOError " + repr(E)
        else:
            return 0

        # 2. try to load font from pinobot Default Font
        try:
            self.main_font = ImageFont.truetype(
                self.base_path + "/modules/Hardware/Fonts/NanumBarunGothicBold.ttf",
                self.main_font_size,
            )
            self.console_font = ImageFont.truetype(
                self.base_path + "/modules/Hardware/Fonts/NanumBarunGothicBold.ttf",
                self.console_font_size,
            )
        except IOError:
            print("fail to load font, load [system default] ")
        except Exception as E:
            self.last_exception = "OLED.load_font(), No IOError " + repr(E)
        else:
            return 0

        # 3. try to load font from System Default Font
        try:
            self.main_font = ImageFont.load_default()
            self.console_font = ImageFont.load_default()
        except Exception as E:
            self.last_exception = "OLED.load_font(), No IOError " + repr(E)
            return -1
        else:
            return 0

    # [D.3] convert text as binary image using PIL,
    def __text_2_image(self, unicode_text, resize=(128, 64)):
        SPACING = 10

        # 1. split text by newline
        split_text = unicode_text.split("\n")

        # 2. calculate text area
        # find max width and height of lines
        widths = []
        heights = []
        for line in split_text:
            width, height = self.main_font.getsize(line)
            widths.append(width)
            heights.append(height)

        max_width = max(widths)
        max_height = sum(heights) + SPACING * (len(split_text) - 1)

        # 3. make new image by font size
        image = Image.new("L", (max_width, max_height))
        draw = ImageDraw.Draw(image)

        # 4. draw text to image
        draw.text(
            (0, 0),
            unicode_text,
            font=self.main_font,
            fill=255,
            spacing=SPACING,
            align="center",
        )

        # 5. change to binary image and return it.
        return image.resize(resize, resample=Image.LANCZOS).convert("1")

    # [D.4] Draw progress line to image
    @staticmethod
    def __draw_line(draw, step):
        length = 12
        y0 = 4 * (15 - step) + 3
        y1 = y0
        x0 = 1
        x1 = length - x0
        draw.line(xy=[(x0, y0), (x1, y1)], fill=255, width=3)
