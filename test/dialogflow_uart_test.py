import unittest


class MyTestCase(unittest.TestCase):
    def test_something(self):
        from modules.Cloud.Google.pino_dialogflow import PinoDialogFlow
        from modules.Hardware.pino_uart import Pino_UART
        import time , logging

        log = logging.getLogger("Main")
        log.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "[%(levelname)s] (%(asctime)s : %(filename)s:%(lineno)d) > %(message)s"
        )
        log_console = logging.StreamHandler()
        log_console.setFormatter(formatter)
        log.addHandler(log_console)

        DIALOGFLOW_PROJECT_ID = "squarebot01-yauqxo"
        DIALOGFLOW_LANGUAGE_CODE = "ko"
        GOOGLE_APPLICATION_CREDENTIALS = (
            "/home/pi/Desktop/PinoBot/keys/squarebot01-yauqxo-27c0bd80da2b.json"
        )
        TIME_OUT = 7

        Gbot = PinoDialogFlow(
            DIALOGFLOW_PROJECT_ID,
            DIALOGFLOW_LANGUAGE_CODE,
            GOOGLE_APPLICATION_CREDENTIALS,
            TIME_OUT,
            log
        )
        Gbot.open_session()

        uart = Pino_UART()
        uart.write("ready")

        print('ready to test')
        time.sleep(1)

        print("[case 1]. send event_result to arduino ")
        result1 = Gbot.send_event("Wall_Event", {"Wall_time": 50})
        uart.write(pino_response=result1)
        input("[case 1]. check uart result from arduino")
        print("[case 1]. Done! \n\n")

        print("[case 2]. send streaming result to arduino ")
        print("[case 2]  start stream :")
        Gbot.start_stream()
        result2 = Gbot.get_stream_response(fail_handler=True)
        Gbot.play_audio_response(result2)
        uart.write(pino_response=result2)
        input("[case 2]. check uart result from arduino")
        print("[case 2]. Done! \n\n")

        print("[case 3]. get event parameter from arduino and send to dialogflow ")
        print("wait..")
        while True:
            msg_from_arduino = uart.read()
            if msg_from_arduino is None:
                print(".",end='')
            else :
                print("gotcha! : ",msg_from_arduino)
                result3 = Gbot.send_event(msg_from_arduino['event_name'],msg_from_arduino)
                break

        Gbot.play_audio_response(result3)
        uart.write(pino_response=result3)
        print("[case 3]. Done! \n\n")


        print("[case 4]. do loop with read and write ")
        for i in range(10):
            print("[case 4] loop %d in 10"%(i+1))
            msg_from_arduino = uart.read()
            if msg_from_arduino is not None:
                print("[case 4] gotcha! : ",msg_from_arduino)
                result4 = Gbot.send_event(msg_from_arduino['event_name'],msg_from_arduino)
                Gbot.play_audio_response(result4)
                uart.write(pino_response=result4)
            else :
                print("[case 4] start stream :")
                Gbot.start_stream()
                result5 = Gbot.get_stream_response(fail_handler=True)
                Gbot.play_audio_response(result5)
                uart.write(pino_response=result5)
        print("[case 4]. Done! \n\n")

        print("finish")

if __name__ == '__main__':
    unittest.main()
