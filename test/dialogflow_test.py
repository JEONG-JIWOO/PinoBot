import unittest


class MyTestCase(unittest.TestCase):
    def test_something(self):
        # 1. init test
        from modules.Cloud.Google.pino_dialogflow import PinoDialogFlow

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
        )
        Gbot.open_session()

        # 2. function test
        print("\n\n Start!")
        result = Gbot.send_text("안녕하세요")
        print(result)

        Gbot.start_stream()
        print("Streaming started, say something timeout, %d seconds" % TIME_OUT)
        result = Gbot.get_stream_response(fail_handler=True)
        Gbot.play_audio_response(result)
        print(result)

        # Gbot.play_audio_response(tts)
        print("\n\n Start!")
        result =Gbot.send_event("Wall_Event", {"Wall_time": 50})
        Gbot.play_audio_response(result)
        print(result)




if __name__ == '__main__':
    unittest.main()
