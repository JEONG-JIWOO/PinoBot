"""
Module TEST codes

Core.Hardware.SPI.Pino_LED
"""

import unittest ,time

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

def custom_function_1():
    from Core.Cloud.Google.pino_dialogflow import PinoDialogFlow
    # 1. Set google dialogflow project config
    DIALOGFLOW_PROJECT_ID = 'a2-bwogyf'
    DIALOGFLOW_LANGUAGE_CODE = 'ko'
    GOOGLE_APPLICATION_CREDENTIALS = '/home/pi/Desktop/PinoBot/Keys/a2-bwogyf-c40e46d0dc2b.json'
    TIME_OUT = 7

    # 2. init and connect dialogflow project
    Gbot = PinoDialogFlow(DIALOGFLOW_PROJECT_ID,
                          DIALOGFLOW_LANGUAGE_CODE,
                          GOOGLE_APPLICATION_CREDENTIALS,
                          TIME_OUT)
    Gbot.open_session()

    # 3. sent text and get Response
    print("\n\n Start!")
    text_response = Gbot.send_text("안녕하세요")
    print("[Q] : %s " % text_response.query_result.query_text)
    print("[A] : accuracy:%0.3f | %s " % (text_response.query_result.intent_detection_confidence,
                                          text_response.query_result.fulfillment_text))
    Gbot.play_audio(text_response)

    # 4. send voice and get voice response
    Gbot.start_stream()
    print("Streaming started, say something timeout, %d seconds" % TIME_OUT)
    stt_response, chatbot_response, tts = Gbot.get_response()
    if stt_response is not None and chatbot_response is not None:
        print("[Q] : %s " % stt_response.recognition_result.transcript)
        print("[A] : accuracy:%0.3f | %s " % (chatbot_response.query_result.intent_detection_confidence,
                                              chatbot_response.query_result.fulfillment_text))
    else:
        print("rec error")
    # [WIP]
    # play audio_binary file..
    Gbot.play_audio(tts)

    # 5. send Event with parameters
    print("\n\n Start!")
    event_response = Gbot.send_event("Wall_Event", {'Wall_time': 50})
    print("[Q] : %s " % event_response.query_result.query_text)
    print("[A] : accuracy:%0.3f | %s " % (event_response.query_result.intent_detection_confidence,
                                          event_response.query_result.fulfillment_text))

    # 6. session Tester,
    cnt = 0
    """
    while True:
        time.sleep(5)
        cnt += 5
        print('%d seconds went. ' % cnt)
        if cnt % 2400 == 0:
            try:
                text_response = Gbot.send_text("안녕하세요")
                print("[Q] : %s " % text_response.query_result.query_text)
                print("[A] : accuracy:%0.3f | %s " % (text_response.query_result.intent_detection_confidence,
                                                      text_response.query_result.fulfillment_text))
            except:
                print("session Error")
    """

def custom_function_2():
    from Core.Cloud.Google.pino_dialogflow import PinoDialogFlow
    DIALOGFLOW_PROJECT_ID = 'squarebot01-yauqxo'
    DIALOGFLOW_LANGUAGE_CODE = 'ko'
    GOOGLE_APPLICATION_CREDENTIALS = '/home/pi/Desktop/PinoBot/Keys/squarebot01-yauqxo-8d211b1f1a85.json'
    TIME_OUT = 7

    # 2. init and connect dialogflow project
    Gbot = PinoDialogFlow(DIALOGFLOW_PROJECT_ID,
                          DIALOGFLOW_LANGUAGE_CODE,
                          GOOGLE_APPLICATION_CREDENTIALS,
                          TIME_OUT)
    Gbot.open_session()
    print("\n\n Start!")
    text_response = Gbot.send_text("15분 뒤에 알려줘")
    from google.protobuf.json_format import MessageToDict
    a = MessageToDict(text_response.query_result)
    print(a)
    print("-" * 30)
    print("[Q] : %s " % text_response.query_result.query_text)
    print("[A] : accuracy:%0.3f | %s " % (text_response.query_result.intent_detection_confidence,
                                          text_response.query_result.fulfillment_text))
    Gbot.play_audio(text_response)
