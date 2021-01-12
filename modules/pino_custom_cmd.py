#!/usr/bin/python3


def run_pino_custom_cmd(hardware, intent_name, dialogflow_parameters):
    # hardware.write(text="Hello\nWorld!", led=[0, 0, 100], servo_angle=[180, 180, 90], servo_time=2)
    print("hi")
    hardware.write(text="Hello\nWorld!")

    if intent_name == "[Pino] Custom Script Example":
        if "color" in dialogflow_parameters.keys():
            print(dialogflow_parameters["color"])
            if "녹" in dialogflow_parameters["color"]:
                hardware.write(led=[0, 255, 0])
            elif "파랑" in dialogflow_parameters["color"]:
                hardware.write(led=[0, 0, 255])
            elif "빨강" in dialogflow_parameters["color"]:
                hardware.write(led=[255, 0, 0])
            elif "보라" in dialogflow_parameters["color"]:
                hardware.write(led=[255, 0, 255])
            elif "노랑" in dialogflow_parameters["color"]:
                hardware.write(led=[255, 255, 0])
            elif "청록" in dialogflow_parameters["color"]:
                hardware.write(led=[0, 255, 255])
            elif (
                "흰" in dialogflow_parameters["color"]
                or "백" in dialogflow_parameters["color"]
            ):
                hardware.write(led=[255, 255, 255])
            elif "검정" in dialogflow_parameters["color"]:
                hardware.write(led=[0, 0, 0])

    pass
