import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import time

# pip3 install adafruit-circuitpython-ssd1306
# https://github.com/adafruit/Adafruit_CircuitPython_SSD1306

class OLED:
    """
    A. con & deconstruct
    """
    def __init__(self,i2c,base_path,console_font_name="",main_font_name=""):
        # 0. Argument
        self.base_path = base_path
        self.console_font_name = console_font_name
        self.main_font_name = main_font_name
        self.i2c = i2c

        # 1. Static Variables
        self.oled_size = (128, 64)
        self.main_font_size =30
        self.console_font_size = 12

        # 2. variables
        self.last_reset_time = 0
        self.last_exception = ""
        self.console_msg = ""

        # 3. Objects
        self.oled = None
        self.main_font = None
        self.console_font = None
        self.im = None

        # 4. Init Functions
        self.reset()

    def __del__(self):
        # noinspection PyBroadException
        try:
            del self.oled  # Deconstruct Object
            del self.main_font
        except:
            pass
    """
    B. reset 
    """
    def reset(self):
        # 1. check last reset time,
        #    only can reset after 1min after last reset
        if (time.time() - self.last_reset_time) < 60:
            return 0

        # 2. if self.serial exists..
        if self.oled is not None:
            try:
                del self.oled     # Deconstruct Object
                del self.main_font
            except Exception as E:
                self.last_exception = "OLED.reset(), # 2. del " + repr(E)


        # 3. refresh last reset time
        self.last_reset_time = time.time()

        # 4. re open Serial
        try:
            self.oled = adafruit_ssd1306.SSD1306_I2C(self.oled_size[0], self.oled_size[1], self.i2c)
            self.oled.fill(0)
            self.oled.show()
            self.__load_font()
        except Exception as E:
            self.last_exception = "OLED.reset(), # 4. remake " + repr(E)
            return -1
    """
    C. Public Functions
    """
    # [C.1] find image by "image_name', from directory, and send to OLED
    def send_image(self,image_name):
        # 1. load image
        r = self.__load_image(image_name)
        if r != 0:
            return r
        # 2. try to send
        try :
            self.oled.image(self.im)
            self.oled.show()
        # 3. Fail to send data
        except Exception as E :
            self.last_exception = str(E)
            self.reset()
            return -1
        # 4. Success to send data
        else :
            return 0

    # [C.2] convert "text" to image, and send to OLED
    # NOTE : Progress bar : NO,    text : variable size
    def send_text(self,text):
        # 1. make image from text
        try :
            self.__text_2_image(text)
        except Exception as E:
            self.last_exception = "OLED.text_2_image()" + repr(E)
            return -1
        # 2. try to send
        try :
            self.oled.image(self.im)
            self.oled.show()
        # 3. Fail to send data
        except Exception as E :
            self.last_exception = str(E)
            self.reset()
            return -1
        # 4. Success to send data
        else :
            return 0

    # [C.3] show progress "step" , convert "msg" to image, and send to OLED
    # NOTE : Progress bar : YES,    text : Fixed size
    def send_console(self, step, msgs, mode = "a"):
        # 1. make new image by font size
        im = Image.new("L", (128,64), 0)
        draw = ImageDraw.Draw(im)

        if mode == "a":
            self.console_msg += msgs
            #print(self.console_msg)
        else :
            self.console_msg = msgs

        # 2. draw text to image
        draw.text((18, 0), self.console_msg, font=self.console_font, fill=255, spacing=2, align="left")
        if step > 16:
            step = 16
        for i in range(step):
            self.__draw_line(draw, i)

        # 3. change to binary image and save it.
        self.im = im.convert("1")
        try :
            self.oled.image(self.im)
            self.oled.show()
        # 4. Fail to send data
        except Exception as E :
            self.last_exception = str(E)
            self.reset()
            return -1
        # 5. Success to send data
        else :
            return 0

    # [C.4] show progress "step" , convert "msg" to image, and send to OLED
    # NOTE : Progress bar : YES,    text : variable size
    def send_loading(self, step = 0, ratio = 0, msg =""):
        progress_im = Image.new("L", self.oled_size, 0)
        draw = ImageDraw.Draw(progress_im)

        if step == 0 :
            now_step = int(ratio * 0.16)
            for i in range(now_step):
                self.__draw_line(draw, i)

        elif step > 0:
            if step > 16:
                step = 16
            for i in range(step):
                self.__draw_line(draw, i)

        if msg != "":
            self.__text_2_image(msg, resize=(110, 64))
            progress_im.paste(self.im,(18,0))

        self.im = progress_im.convert("1")
        self.oled.image(self.im)
        self.oled.show()

    """
    D. Private Functions
    """
    # [D.1] load font by name, from directory
    def __load_font(self):
        # 1. try to load font from config file

        try :
            self.main_font = ImageFont.truetype(self.base_path+"/Core/Hardware/Fonts/"+self.main_font_name,
                                                self.main_font_size)
            self.console_font = ImageFont.truetype(self.base_path+"/Core/Hardware/Fonts/"+self.console_font_name,
                                                   self.console_font_size)
        except IOError :
            print("fail to load font, load [NanumBarunGothicBold] ")
        except Exception as E:
            self.last_exception = "OLED.load_font(), No IOError " + repr(E)
        else :
            return 0

        # 2. try to load font from pinobot Default Font
        try :
            self.main_font = ImageFont.truetype(
                                self.base_path+"/Core/Hardware/Fonts/NanumBarunGothicBold.ttf",
                                self.main_font_size)
            self.console_font = ImageFont.truetype(
                                self.base_path+"/Core/Hardware/Fonts/NanumBarunGothicBold.ttf",
                                self.console_font_size)
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
            return -2
        else:
            return 0

    # [D.2] load image form directory
    def __load_image(self, image_name):
        try :
            path = self.base_path+"media/image/"+image_name
            image = Image.open(path)
            im = image.resize(self.oled_size)
            # 2. change to binary image and save it.
            self.im = im.convert("1")
        except FileNotFoundError as E:
            self.last_exception = "OLED.load_image() " + repr(E)
            return -2
        except Exception as E :
            self.last_exception = "OLED.load_image() " + repr(E)
            return -1

    # [D.3] convert text as binary image using PIL,
    def __text_2_image(self, unicode_text, resize = (128, 64)):
        # 1. split text by newline
        split_text = unicode_text.split("\n")

        # 2. calculate text area
        max_text_weight = 0  # find MAX weight of lines
        max_text_height = 0  # find MAX height of lines
        for line in split_text:
            size = self.main_font.getsize(line)
            if size[0] > max_text_weight:
                max_text_weight = size[0]
            if size[1] > max_text_height:
                max_text_height = size[1]
        space = 10
        new_line_cnt = unicode_text.count("\n") + 1
        image_size = [max_text_weight, max_text_height + space]

        # 3. make new image by font size
        im = Image.new("L", (image_size[0], image_size[1] * new_line_cnt), 0)
        draw = ImageDraw.Draw(im)

        # 4. draw text to image
        draw.text((0, 0), unicode_text, font=self.main_font, fill=255, spacing=space, align="center")

        # 5. change to binary image and save it.
        im = im.resize(resize,resample=Image.LANCZOS)
        self.im = im.convert("1")
        return 0

    # [D.4] Draw progress line to image
    @staticmethod
    def __draw_line(draw, step):
        length = 12
        y0 = 4 * (15 - step) + 3
        y1 = y0
        x0 = 1
        x1 = length - x0
        draw.line(xy=[(x0, y0), (x1, y1)], fill=255, width=3)


"""
Module TEST codes 
"""
def test():
    i2c = board.I2C()
    oled_board = OLED(i2c,
                      "/home/pi/Desktop/PinoBot/",
                      'NanumSquareEB.ttf',
                      'NanumSquareEB.ttf')

    for i in range(15):
        oled_board.send_loading(ratio=7 * i, msg =" PrePare Boot\n \n WAIT..")
        time.sleep(0.02)
    oled_board.send_loading(100)
    time.sleep(1)
    oled_board.send_loading()

    for i in range(15):
        if i < 5:
            if i % 2 == 0 :
                oled_board.send_console(step=i,msgs=" loading A")
            else :
                oled_board.send_console(step=i, msgs=".")
            time.sleep(0.2)
        elif i < 10:
            if i % 2 == 0 :
                oled_board.send_console(step=i, msgs="\n loading B")
            else :
                oled_board.send_console(step=i, msgs=".")
            time.sleep(0.2)
        elif i < 15:
            if i % 2 == 0 :
                oled_board.send_console(step=i, msgs="\n loading C")
            else :
                oled_board.send_console(step=i, msgs=".")

            time.sleep(0.2)
    oled_board.send_console(step=15, msgs="Total Done.",mode="w")

if __name__ == '__main__':
    test()