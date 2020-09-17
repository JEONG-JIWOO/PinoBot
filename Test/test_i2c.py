"""
Module TEST codes

Core.Hardware.SPI.Pino_LED
"""

import unittest

def custom_function_1():
    # 1. init test
    import board ,time
    from Core.Hardware.I2C import pino_oled
    i2c = board.I2C()
    oled_board = pino_oled.Pino_OLED(i2c,
                      "/home/pi/Desktop/PinoBot/",
                      'NanumSquareEB.ttf',
                      'NanumSquareEB.ttf')

    # 2. working test
    for i in range(15):
        oled_board.send_loading_text(ratio=7 * i, msg =" PrePare Boot\n \n WAIT..")
        time.sleep(0.02)
    oled_board.send_loading_text(100)
    time.sleep(1)
    oled_board.send_loading_text()

    for i in range(15):
        if i < 5:
            if i % 2 == 0 :
                oled_board.send_loading_console(step=i, msgs=" loading A")
            else :
                oled_board.send_loading_console(step=i, msgs=".")
            time.sleep(0.2)
        elif i < 10:
            if i % 2 == 0 :
                oled_board.send_loading_console(step=i, msgs="\n loading B")
            else :
                oled_board.send_loading_console(step=i, msgs=".")
            time.sleep(0.2)
        elif i < 15:
            if i % 2 == 0 :
                oled_board.send_loading_console(step=i, msgs="\n loading C")
            else :
                oled_board.send_loading_console(step=i, msgs=".")

            time.sleep(0.2)
    oled_board.send_loading_console(step=14, msgs="Pyaudio test.", mode="w")
    run_pyaudio()
    oled_board.send_loading_console(step=15, msgs="Total Done.", mode="w")


    # 3. reset test
    oled_board.reset()

    # 4. working after reset test
    for i in range(15):
        oled_board.send_loading_text(ratio=7 * i, msg=" PrePare Boot\n \n WAIT..")
        time.sleep(0.02)
    oled_board.send_loading_text(100)
    time.sleep(1)
    oled_board.send_loading_text()

    for i in range(15):
        if i < 5:
            if i % 2 == 0:
                oled_board.send_loading_console(step=i, msgs=" loading A")
            else:
                oled_board.send_loading_console(step=i, msgs=".")
            time.sleep(0.2)
        elif i < 10:
            if i % 2 == 0:
                oled_board.send_loading_console(step=i, msgs="\n loading B")
            else:
                oled_board.send_loading_console(step=i, msgs=".")
            time.sleep(0.2)
        elif i < 15:
            if i % 2 == 0:
                oled_board.send_loading_console(step=i, msgs="\n loading C")
            else:
                oled_board.send_loading_console(step=i, msgs=".")

            time.sleep(0.2)
    oled_board.send_loading_console(step=15, msgs="Total Done.", mode="w")

    # 5. del test
    del oled

def custom_function_2():
    # 1. init test
    import board ,time
    from Core.Hardware.I2C import pino_servo
    i2c = board.I2C()
    servo_board = pino_servo.Pino_SERVO(i2c)

    # 2. working test
    time.sleep(1)
    servo_board.write([0, 0, 0, 0, 0], 4)
    run_pyaudio()
    servo_board.write([180], 2)
    servo_board.write([1], 2)


    # 3. reset test
    servo_board.reset()

    # 4. working after reset test
    time.sleep(1)
    servo_board.write([0, 0, 0, 0, 0], 4)
    run_pyaudio()
    servo_board.write([180], 2)
    servo_board.write([1], 2)

    # 5. del test
    del servo_board

def run_pyaudio():
    import pyaudio
    import wave

    servo_board.write([100, 90, 80, 70, 60, 30, 32], 0.1)
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16, channels=1,
                             rate=16000, input=True,
                             frames_per_buffer=2048, input_device_index=2)

    a = stream.read(2048, exception_on_overflow = False)
    print(a)
    stream.close()

    wav_data = wave.open("./1.wav", "rb")
    # Open play stream. Formats are fixed,
    stream = audio.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=16000,
        output=True
    )

    # Play wav file.
    data = wav_data.readframes(2048)
    while len(data) > 1:
        stream.write(data)
        data = wav_data.readframes(2048)
    stream.stop_stream()
    stream.close()
    audio.terminate()


class CustomTests(unittest.TestCase):
    def setUp(self):
        """ 테스트 시작전 테스트 설정"""
        pass

    def tearDown(self):
        """ 테스트 끝난이후 실행되는 함수"""
        pass

    def test_runs(self):
        """ 실 테스트 코드 """
        custom_function_1()
        custom_function_2()

if __name__ == '__main__':
    unittest.main()
