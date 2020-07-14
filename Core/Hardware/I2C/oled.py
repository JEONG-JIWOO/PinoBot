import board
import digitalio
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import adafruit_ssd1306
import time

# pip3 install adafruit-circuitpython-ssd1306
# https://github.com/adafruit/Adafruit_CircuitPython_SSD1306

class OLED():
    def __init__(self,i2c, font_name = "NanumBarunGothicBold.ttf"):
        # 0. Argument
        self.font_path ="/home/pi/Desktop/PinoBot/Core/Hardware/Fonts/"+font_name
        self.i2c = i2c

        # 1. Static Variables
        self.oled_size = (128, 64)

        # 2. variables
        self.last_reset_time = 0
        self.last_exception = ""

        # 3. Objects
        self.oled = None
        self.unicode_font = None
        self.consol_font = None
        self.im = None

        # 4. Init Functions
        self.reset()

    def __del__(self):
        try:
            del self.oled  # Deconstruct Object
            del self.unicode_font
        except:
            pass

    def reset(self):
        # 1. check last reset time,
        #    only can reset after 1min after last reset
        if (time.time() - self.last_reset_time) < 60:
            return 0

        # 2. if self.serial exists..
        if self.oled is not None:
            try:
                del self.oled     # Deconstruct Object
                del self.unicode_font
            except:
                pass

        # 3. refresh last reset time
        self.last_reset_time = time.time()

        # 4. re open Serial
        try:
            self.oled = adafruit_ssd1306.SSD1306_I2C(self.oled_size[0], self.oled_size[1], self.i2c)
            self.oled.fill(0)
            self.oled.show()
            self.load_font()
        except Exception as E:
            self.last_exception = "OLED.reset(), No IOError " + repr(E)
            return -1

    def load_font(self):
        # 1. try to load font from config file
        try :
            self.unicode_font = ImageFont.truetype(self.font_path, 30)
            self.consol_font = ImageFont.truetype(self.font_path, 14)
        except IOError :
            print("fail to load font, load [NanumBarunGothicBold] ")
        except Exception as E:
            self.last_exception = "OLED.load_font(), No IOError " + repr(E)
            return -2
        else :
            return 0

        # 2. try to load font from pinobot Default Font
        try :
            self.unicode_font = ImageFont.truetype(
                                "/home/pi/Desktop/PinoBot/Core/Hardware/Fonts/NanumBarunGothicBold.ttf", 30)
            self.consol_font = ImageFont.truetype(
                "/home/pi/Desktop/PinoBot/Core/Hardware/Fonts/NanumBarunGothicBold.ttf", 14)
        except IOError:
            print("fail to load font, load [system default] ")
        except Exception as E:
            self.last_exception = "OLED.load_font(), No IOError " + repr(E)
            return -2
        else:
            return 0

        # 3. try to load font from System Default Font
        try:
            self.unicode_font = ImageFont.load_default()
        except Exception as E:
            self.last_exception = "OLED.load_font(), No IOError " + repr(E)
            return -2
        else:
            return 0

    def send_image(self,image_name):
        # 1. load image
        r = self._load_image(image_name)
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

    def send_text(self,text):
        # 1. make image from text
        try :
            self._text_2_image(text)
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

    def send_console(self, step, console_msgs):
        # 3. make new image by font size
        im = Image.new("L", (128,64), (0))
        draw = ImageDraw.Draw(im)

        # 4. draw text to image
        draw.text((18, 0), console_msgs, font=self.consol_font, fill=(255), spacing=2,align="left")
        if step > 16:
            step = 16
        for i in range(step):
            self._draw_line(draw, i)

        # 5. change to binary image and save it.
        self.im = im.convert("1")
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

    def _load_image(self, image_name):
        try :
            path = "/home/pi/Desktop/PinoBot/media/image/"+image_name
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

    def _text_2_image(self,unicode_text,resize = (128,64)):
        # 1. split text by newline
        splited_text = unicode_text.split("\n")

        # 2. calculate text area
        max_text_weight = 0  # find MAX weight of lines
        max_text_height = 0  # find MAX height of lines
        for line in splited_text:
            size = self.unicode_font.getsize(line)
            if size[0] > max_text_weight:
                max_text_weight = size[0]
            if size[1] > max_text_height:
                max_text_height = size[1]
        space = 10
        new_line_cnt = unicode_text.count("\n") + 1
        Image_Size = [max_text_weight, max_text_height + space]

        # 3. make new image by font size
        im = Image.new("L", (Image_Size[0], Image_Size[1] * new_line_cnt), (0))
        draw = ImageDraw.Draw(im)

        # 4. draw text to image
        draw.text((0, 0), unicode_text, font=self.unicode_font, fill=(255), spacing=space, align="center")

        # 5. change to binary image and save it.
        im = im.resize(resize,resample=Image.LANCZOS)
        self.im = im.convert("1")
        return 0

    def loading_scean(self ,step = 0, persent = 0, msg = ""):
        progress_im = Image.new("L", self.oled_size, (0))
        draw = ImageDraw.Draw(progress_im)

        if step == 0 :
            now_step = int(persent * 0.16)
            for i in range(now_step):
                self._draw_line(draw, i)

        elif step > 0:
            if step > 16:
                step = 16
            for i in range(step):
                self._draw_line(draw, i)

        if msg != "":
            self._text_2_image(msg,resize=(110,64))
            progress_im.paste(self.im,(18,0))

        self.im = progress_im.convert("1")
        self.oled.image(self.im)
        self.oled.show()

    def _draw_line(self,draw,step):
        length = 10
        y0 = 4 * (15 - step) + 3
        y1 = y0
        x0 = 1
        x1 = length - x0
        draw.line(xy=[(x0, y0), (x1, y1)], fill=(255), width=3)


def test():
    i2c = board.I2C()
    A = OLED(i2c)
    #A.send_text(" 힘쎄고 좋은아침! \n 내이름을 묻는다면 \n 나는 왈도 ")
    #A.send_image("asdf.jpg")
    print(A.last_exception)

    for i in range(15):
        A.loading_scean(persent=7*i,msg ="로딩중.. \n 대기")
        time.sleep(0.5)
    A.loading_scean(100)
    time.sleep(1)
    A.loading_scean()

    for i in range(15):
        A.loading_scean(step=i)
        time.sleep(0.5)
    A.loading_scean(16)

if __name__ == '__main__':
    test()