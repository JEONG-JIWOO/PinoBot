from PIL import Image, ImageDraw, ImageFont, ImageFilter

import numpy
#configuration

class FontGen():
    def __init__(self):
        self.unicode_font = ImageFont.truetype("/home/pi/pinobot/Core/Hardware/Fonts/TmonMonsori.ttf.ttf", 16)
        self.hex_array = numpy.transpose(numpy.array([16,8,4,2,1]))
    
    def gen(self, unicode_text):
        im  =  Image.new ( "L", (15*16,15), (0) )
        draw  =  ImageDraw.Draw ( im )
        draw.text ( (0,0), unicode_text, font=self.unicode_font, fill=(255))
        im = im.resize((80,8))
        I = numpy.asarray(im)
        
        threshold = 200

        #im = im.point(lambda p: p > threshold and 255)  
        #im.save("text.jpg")

        I = numpy.where(I > threshold, 1,0)
        #I.reshape()
        string = numpy.hsplit(I,16)

        hex_string = []
        for character in string:
            hex_character =[]
            
            for line in character:
                hex_value = numpy.dot(line,self.hex_array)
                hex_character.append(hex_value)
        
            hex_string.append(hex_character)
        return hex_string

        
def example():
    F = FontGen()
    a = F.gen("안녕하세요 저는")
    print(a)


if __name__ == "__main__":
    example()