"""
Module TEST codes
Core.Hardware.SPI.Pino_LED
"""
import unittest, time


def custom_function_1():
    # 1. init test
    from modules.Cloud.Google.pino_dialogflow import PinoDialogFlow

    DIALOGFLOW_PROJECT_ID = "squarebot01-yauqxo"
    DIALOGFLOW_LANGUAGE_CODE = "ko"
    GOOGLE_APPLICATION_CREDENTIALS = (
        "/home/pi/Desktop/PinoBot/keys/pinobot01_example.json"
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
    text_response = Gbot.send_text("안녕하세요")
    print("[Q] : %s " % text_response.query_result.query_text)
    print(
        "[A] : accuracy:%0.3f | %s "
        % (
            text_response.query_result.intent_detection_confidence,
            text_response.query_result.fulfillment_text,
        )
    )
    Gbot.play_audio_response(text_response)

    Gbot.start_stream()
    print("Streaming started, say something timeout, %d seconds" % TIME_OUT)
    stt_response, chatbot_response, tts = Gbot.get_response()
    if stt_response is not None and chatbot_response is not None:
        print("[Q] : %s " % stt_response.recognition_result.transcript)
        print(
            "[A] : accuracy:%0.3f | %s "
            % (
                chatbot_response.query_result.intent_detection_confidence,
                chatbot_response.query_result.fulfillment_text,
            )
        )

    else:
        print("rec error")
    # Gbot.play_audio_response(tts)
    print("\n\n Start!")
    event_response = Gbot.send_event("Wall_Event", {"Wall_time": 50})
    print("[Q] : %s " % event_response.query_result.query_text)
    print(
        "[A] : accuracy:%0.3f | %s "
        % (
            event_response.query_result.intent_detection_confidence,
            event_response.query_result.fulfillment_text,
        )
    )

    # 3. reset test
    Gbot.reset()

    # 4. function test after reset
    print("\n\n Start!")
    text_response = Gbot.send_text("안녕하세요")
    print("[Q] : %s " % text_response.query_result.query_text)
    print(
        "[A] : accuracy:%0.3f | %s "
        % (
            text_response.query_result.intent_detection_confidence,
            text_response.query_result.fulfillment_text,
        )
    )
    Gbot.play_audio_response(text_response)

    Gbot.start_stream()
    print("Streaming started, say something timeout, %d seconds" % TIME_OUT)
    stt_response, chatbot_response, tts = Gbot.get_response()
    if stt_response is not None and chatbot_response is not None:
        print("[Q] : %s " % stt_response.recognition_result.transcript)
        print(
            "[A] : accuracy:%0.3f | %s "
            % (
                chatbot_response.query_result.intent_detection_confidence,
                chatbot_response.query_result.fulfillment_text,
            )
        )
    else:
        print("rec error")
    Gbot.play_audio_response(tts)
    print("\n\n Start!")
    event_response = Gbot.send_event("Wall_Event", {"Wall_time": 50})
    print("[Q] : %s " % event_response.query_result.query_text)
    print(
        "[A] : accuracy:%0.3f | %s "
        % (
            event_response.query_result.intent_detection_confidence,
            event_response.query_result.fulfillment_text,
        )
    )

    # 5. del test
    del Gbot


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


if __name__ == "__main__":
    unittest.main()
