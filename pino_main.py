from modules import pinobot
import time

if __name__ == "__main__":
    bot  = pinobot.PinoBot()
    bot.hardware.write(text="대기중..")
    while True:
        bot.update()

        # case 1, sensor on
        if bot.state == pinobot.PinoState.SENSOR_ON:

            # start listen
            response = bot.listen()

            # listen success,
            if response is not None:
                bot.hardware.write(text="음성인식 완료!")
                bot.start_say(response)
                bot.start_act(response)
                bot.wait_say_and_act()      # wait until say and act
                print(response.stt_result,"  |  ", response.intent_name,response.intent_response)
                bot.return_idle()           # return to idle state

            # listen failed
            else :
                bot.hardware.write(text="음성인식 실패 ㅠㅠ")
                time.sleep(3)
                bot.return_idle()

        # case 2, uart[serial] communication on
        elif bot.state == pinobot.PinoState.UART_ON:

            # Get event from dialogflow
            response = bot.call_uart_event()

            # success,
            if response is not None:
                bot.hardware.write(text = "메세지 확인!")
                bot.start_act(response)
                bot.start_say(response)
                bot.wait_say_and_act()      # wait until say and act
                print(response.stt_result, "  |  ", response.intent_name, response.intent_response)
                bot.return_idle()           # return to idle state

            # failed
            else:
                bot.hardware.write(text="메세지 잘못보냄 ㅠㅠ")
                time.sleep(0.5)

        time.sleep(0.05) # sleep for 50ms to reduce cpu use