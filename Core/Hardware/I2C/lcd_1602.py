import smbus
import time
from Core.Hardware.I2C.fontgen import FontGen
from Core.Hardware.I2C.RPi_I2C_driver import lcd
"""
https://github.com/sterlingbeason/LCD-1602-I2C

"""


class LCD1602():
    def __init__(self,address):
        self.lcd = lcd(address)
        self.lcd.display()
        self.send_msg("LCD start")
        #self.F = FontGen()

    def __del__(self):
        self.lcd.clear() # clear LCD display
        self.lcd.noDisplay()
        pass

    def send_msg(self,msg):
        
        if len(msg) < 17: # only, line 0
            self.fast_clear(0)
            self.lcd.setCursor(0,0)
            self.lcd.print(msg)

        else : # line1 and line2
            line1 = msg[0:16]
            line2 = msg[16:]
            
            self.fast_clear(0)
            self.lcd.setCursor(0,0)
            self.lcd.print(line1)

            self.fast_clear(1)
            self.lcd.setCursor(0,1)
            self.lcd.print(line2)    
        
    def fast_clear(self,line):
        # lcd.clear() is too slow, make alternate fuction
        if line == 0:
            self.lcd.setCursor(0,0)    
            self.lcd.print("                ")
        elif line == 0:
            self.lcd.setCursor(0,1)    
            self.lcd.print("                ")

    """
    def send_hangul(self,msg):
        self.lcd.clear()
        self.lcd.setCursor(0,0)
        characters = self.F.gen(msg)
        
        for i in range(8):
            self.lcd.createChar(i,characters[i])
            self.lcd.setCursor(i,0)
            self.lcd.write(i)
            time.sleep(0.4)
        
        for i in range(8):
            self.lcd.setCursor(i,0)
            self.lcd.write(" ")
            time.sleep(0.05)

            self.lcd.createChar(i,characters[i+8])
            self.lcd.setCursor(i+8,0)
            self.lcd.write(i)
            time.sleep(0.4)
    """

def example():
    LCD = LCD1602(0x27)

    #LCD.send_hangul("잘 보였으면 ")
    #time.sleep(2)
    LCD.send_msg("Ok, just use english")
    time.sleep(2)
    

    #LCD.send_msg("asdassad asd asdasdas da")
    #time.sleep(2)
    

if __name__ == "__main__":
    example()





"""


    lcd =  RPi_I2C_driver.lcd(0x27) # params available for rPi revision, I2C Address, and backlight on/off
    
    # 1. display english
    lcd.print("Hellssssssssssssssssssssssssssssssso")
    time.sleep(1) # wait 5 seconds

    
    # 2. display 한글 only 8character

    F = FontGen()
    a = F.gen("안녕하세요 저는 ㅇㅇ 입니다.")
    
    for i in range(8):
        lcd.createChar(i,a[i])
        
    for i in range(8):
        lcd.setCursor(i,0)
        lcd.write(i)
        time.sleep(0.6)

class LCD:
    def __init__(self, pi_rev = 2, i2c_addr = 0x27, backlight = True):

        # device constants
        self.I2C_ADDR  = i2c_addr
        self.LCD_WIDTH = 16   # Max. characters per line

        self.LCD_CHR = 1 # Mode - Sending data
        self.LCD_CMD = 0 # Mode - Sending command

        self.LCD_LINE_1 = 0x80 # LCD RAM addr for line one
        self.LCD_LINE_2 = 0xC0 # LCD RAM addr for line two

        if backlight:
            # on
            self.LCD_BACKLIGHT  = 0x08
        else:
            # off
            self.LCD_BACKLIGHT = 0x00

        self.ENABLE = 0b00000100 # Enable bit

        # Timing constants
        self.E_PULSE = 0.0005
        self.E_DELAY = 0.0005

        # Open I2C interface
        if pi_rev == 2:
            # Rev 2 Pi uses 1
            self.bus = smbus.SMBus(1)
        elif pi_rev == 1:
            # Rev 1 Pi uses 0
            self.bus = smbus.SMBus(0)
        else:
            raise ValueError('pi_rev param must be 1 or 2')

        # Initialise display7
        self.lcd_byte(0x33, self.LCD_CMD) # 110011 Initialise
        self.lcd_byte(0x32, self.LCD_CMD) # 110010 Initialise
        self.lcd_byte(0x06, self.LCD_CMD) # 000110 Cursor move direction
        self.lcd_byte(0x0C, self.LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
        self.lcd_byte(0x28, self.LCD_CMD) # 101000 Data length, number of lines, font size
        self.lcd_byte(0x01, self.LCD_CMD) # 000001 Clear display

    def lcd_byte(self, bits, mode):
        # Send byte to data pins
        # bits = data
        # mode = 1 for data, 0 for command

        bits_high = mode | (bits & 0xF0) | self.LCD_BACKLIGHT
        bits_low = mode | ((bits<<4) & 0xF0) | self.LCD_BACKLIGHT

        # High bits
        self.bus.write_byte(self.I2C_ADDR, bits_high)
        self.toggle_enable(bits_high)

        # Low bits
        self.bus.write_byte(self.I2C_ADDR, bits_low)
        self.toggle_enable(bits_low)

    def toggle_enable(self, bits):
        time.sleep(self.E_DELAY)
        self.bus.write_byte(self.I2C_ADDR, (bits | self.ENABLE))
        time.sleep(self.E_PULSE)
        self.bus.write_byte(self.I2C_ADDR,(bits & ~self.ENABLE))
        time.sleep(self.E_DELAY)

    def message(self, string, line = 1):
        # display message string on LCD line 1 or 2
        if line == 1:
            lcd_line = self.LCD_LINE_1
        elif line == 2:
            lcd_line = self.LCD_LINE_2
        else:
            raise ValueError('line number must be 1 or 2')

        string = string.ljust(self.LCD_WIDTH," ")

        self.lcd_byte(lcd_line, self.LCD_CMD)

        for i in range(self.LCD_WIDTH):
            self.lcd_byte(ord(string[i]), self.LCD_CHR)

    def clear(self):
        # clear LCD display
        self.lcd_byte(0x01, self.LCD_CMD)

    def createChar(self, location, charmap = []):
        location &= 0x7 # we only have 8 locations 0-7
        self.lcd_byte(0x40 | (location << 3),self.LCD_CMD)
        for i in range(8):
            self.lcd_byte(charmap[i],self.LCD_CHR)
    
    def setCursor(self, col, row):
      if row == 0:
         row_value = self.LCD_LINE_1
      elif row == 1:
         row_value = self.LCD_LINE_2

      self.lcd_byte(0x80| (row_value  + col),self.LCD_CMD)
"""
