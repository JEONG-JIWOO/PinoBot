import unittest

def run_pyaudio():
    import pyaudio
    import wave

    audio = pyaudio.PyAudio()
    info = audio.get_host_api_info_by_index(0)
    num_devices = info.get("deviceCount")

    # 2. find  sound card from index
    sound_card = 0
    card_name = "2mic"  # "2mic" in sound card name
    for i in range(0, num_devices):
        print(audio.get_device_info_by_host_api_device_index(0, i))
        if (audio.get_device_info_by_host_api_device_index(0, i).get(
                "maxInputChannels")) > 0 and card_name in audio.get_device_info_by_host_api_device_index(0, i).get(
                "name"):
            sound_card = i

    print("sound_card :",sound_card )

    stream = audio.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=16000,
        input=True,
        frames_per_buffer=2048,
        input_device_index=sound_card ,
    )

    a = stream.read(2048, exception_on_overflow=False)

    print(a[0:10])

    stream.close()

    wav_data = wave.open("/home/pi/1.wav", "rb")
    # Open play stream. Formats are fixed,
    stream = audio.open(format=audio.get_format_from_width(wav_data.getsampwidth()),
                             channels=wav_data.getnchannels(), rate=wav_data.getframerate(), output=True,
                             output_device_index=sound_card)

    # Play wav file.
    print("play")
    data = wav_data.readframes(2048)
    while len(data) > 1:
        stream.write(data)
        data = wav_data.readframes(2048)
    stream.stop_stream()
    stream.close()
    wav_data.close()
    audio.terminate()  #aplay -D plughw:1,0

class MyTestCase(unittest.TestCase):
    def test_hardware(self):
        print("#6 [ all hardware module ]")
        from modules.Hardware.v1 import Hardware
        import configparser , logging

        run_pyaudio()

        config = configparser.ConfigParser()
        with open("/home/pi/Desktop/PinoBot/etc/pino_config.ini") as fp:
            config.read_file(fp)

        log = logging.getLogger("Main")
        log_console = logging.StreamHandler()
        formatter = logging.Formatter(
            "[%(levelname)s] (%(asctime)s : %(filename)s:%(lineno)d) > %(message)s"
        )
        log_console.setFormatter(formatter)
        log.addHandler(log_console)

        hardware = Hardware(config=config, base_path="/home/pi/Desktop/PinoBot/",log = log)
        hardware.reset()
        hardware.write(
            text="앞으로", led=[0, 0, 100], servo_angle=[45, 45, 90, 29, 60], servo_time=2
        )
        hardware.write(
            text="아래로",
            led=[0, 100, 100],
            servo_angle=[135, 135, 90, 180, 180],
            servo_time=2,
        )
        hardware.write(
            text="위로", led=[255, 255, 255], servo_angle=[0, 0, 0, 10, 10], servo_time=2
        )
        hardware.write(
            text="다시 기본", led=[0, 0, 50], servo_angle=[30, 30, 80, 26, 30], servo_time=2
        )
        hardware.set_default()


    def test_hardware_i2c_servo(self):
        print("#1 [i2c][ servo]")


        # 1. import test
        import board, time
        from modules.Hardware.I2C import pino_servo

        try :
            i2c = board.I2C()
            servo_board = pino_servo.Pino_SERVO(i2c)
        except ValueError:
            print(" check i2c servo connection")
            return 0
        except OSError :
            print(" check i2c servo connection")
            return 0
        except Exception :
            self.assertRaises(Exception)
        else :
            time.sleep(1)
            self.assertEqual(servo_board.write([0, 0, 0, 0, 0], 4), 0)
            self.assertEqual(servo_board.write([100, 90, 80, 70, 60, 30, 32], 0.1), 0)
            run_pyaudio()

    def test_hardware_i2c_oled(self):
        print("#2 [i2c][ oled  ]")

        # 1. import test
        import board, time
        from modules.Hardware.I2C import pino_oled

        # 2. working test
        try :
            i2c = board.I2C()
            oled_board = pino_oled.Pino_OLED(
                i2c, "/home/pi/Desktop/PinoBot/", "NanumSquareEB.ttf", "NanumSquareEB.ttf")
        except ValueError:
            print(" check i2c oled connection")
            return 0
        except OSError :
            print(" check i2c oled connection")
            return 0
        except Exception :
            self.assertRaises(Exception)
        else :
            self.assertEqual(oled_board.send_text("test \n send_text()"),0)
            time.sleep(1)
            self.assertEqual(oled_board.send_loading_text(3,"test \n send_loading_text()"),0)
            time.sleep(1)
            self.assertEqual(oled_board.send_loading_console(3," test \n send_loading_console()"),0)
            time.sleep(1)

    def test_hardware_spi_led(self):
        print("#3 [spi][ led  ]")

        # 1. import test
        from modules.Hardware.SPI import pino_led
        import time
        led = pino_led.Pino_LED()

        # 2. working test
        time.sleep(1)
        self.assertEqual( led.write([100]), 0)
        time.sleep(1)
        self.assertEqual( led.write([100, 100]), 0)
        time.sleep(1)
        self.assertEqual( led.write([100, 100, 100]), 0)
        time.sleep(1)
        self.assertEqual( led.write([100, 100, 100, 100]), 0)
        time.sleep(1)
        self.assertEqual( led.write([100, 100, 100, 100, 100]), 0)
        time.sleep(1)
        self.assertEqual( led.write([100, 100, 100, 100, 100, 100]), 0)

    def test_hardware_gpio(self):
        print("#4 [ gpio ]")

        # 1. init test
        from modules.Hardware import pino_sensor
        import time
        sensor = pino_sensor.Pino_GPIO()

        # 2. working test
        for i in range(30):
            time.sleep(0.1)
            distance = sensor.read_sonic_sensor()
            if distance > 0:
                print("%3.3f cm    %d " % (distance, sensor.volume * 10) + "%")

    def test_hardware_uart(self):
        print("#5 [ uart ]")

        from modules.Hardware.pino_uart import Pino_UART
        import time
        uart = Pino_UART()

        self.assertEqual(uart.write("ready"),0)
        time.sleep(2)


if __name__ == '__main__':
    unittest.main()
