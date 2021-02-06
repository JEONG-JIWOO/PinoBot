#!/usr/bin/python3

import configparser
import subprocess, time
from urllib3 import PoolManager ,Timeout

class PinoBoot:
    """
    A. con & deconstruct
    """

    def __init__(self, base_path):
        # 0. Argument
        # 1. Static Variables
        self.base_path = "/home/pi/Desktop/PinoBot/"  # base_path

        # 2. variables
        self.config_path = self.base_path +"PinoConfig.ini"  # self.base_path+"/config.ini
        )
        self.net_connected = False
        self.error_msg = ""

        # 3. Objects
        self.config = None
        self.hardware = None
        self.cloud = None

    def __del__(self):
        pass

    """
    B. Public Functions
    """
    # [B.1] Actual Function called from outside.
    def boot(self):
        # if boot Failed,
        if self.__main_boot == -1:
            import sys
            sys.exit()

        # boot success
        return self.hardware, self.cloud, self.config

    """
    C. Private , Loading Functions
    """
    # [C.1] main boot sequence
    @property
    def __main_boot(self):
        
        # 2. load ini
        if self.__load_config() == -1:
            try:
                from modules.Hardware.I2C.pino_oled import Pino_OLED
                import board

                i2c = board.I2C()
                oled = Pino_OLED(
                    i2c, self.base_path, "NanumSquareEB.ttf", "NanumSquareEB.ttf"
                )
                oled.send_loading_console(step=1, msgs=self.error_msg)
                with open(self.config_path, "w") as configfile:
                    self.config.write(configfile)
            except:
                # if OLED FAILED , ignore
                pass
            return -1

        # 3. check hardware valid
        if self.__load_hardware() == -1:
            return -1
        self.hardware.OLED.send_loading_console(step=1, msgs="Hardware..OK.\n")

        # 4. check internet connected
        self.__load_internet()

        # 4.1 if not, reset internet
        if not self.net_connected:
            self.__reset_internet()
        self.hardware.OLED.send_loading_console(step=6, msgs="OK. \n")

        # 5. check dialogflow connection
        self.hardware.OLED.send_loading_console(step=8, msgs="DialogFlow")
        if self.__load_diaglogflow() == -1:
            self.hardware.OLED.send_loading_console(step=12, msgs="Fail. \n")
            time.sleep(1)
            self.hardware.OLED.send_loading_console(step=12, msgs="Shutdown Robot")
            return -1
        self.hardware.OLED.send_loading_console(step=13, msgs="OK. \n")

        # 7. Finally all Check ok.
        self.hardware.OLED.send_loading_console(step=16, msgs="Boot OK!")
        return 0

    # [C.2] Config File load & check
    def __load_config(self):
        # 1. config not exist, write default config.
        import os

        default_config = self.__config_default()

        if not os.path.isfile(self.config_path):
            with open(self.config_path, "w") as configfile:
                default_config.write(configfile)

        # 2. try to read config
        try:
            self.config = configparser.ConfigParser()
            with open(self.config_path) as f:
                self.config.read_file(f)
        except Exception as E:
            self.__config_default()
            self.error_msg = "can't read \n config file"
            print("pino_init.__load_config(), " + repr(E))
            return -1

        #  3. check config value is VALID
        check_list = [
            ["int", "GCloud", "time_out"],
            ["int", "MOTOR", "num_motor"],
            ["list", "MOTOR", "motor_enable"],
            ["list", "MOTOR", "motor_min_angle"],
            ["list", "MOTOR", "motor_max_angle"],
            ["list", "MOTOR", "motor_default_angle"],
            ["bool", "LED", "ON"],
            ["int", "GPIO", "sonic_distance"],
            ["int", "GPIO", "sensor_timeout"],
            ["int", "UART", "baud_rate"],
            ["bool", "SleepMode", "state"],
            ["int", "SleepMode", "enter_limit_time"],
            ["float", "SleepMode", "task_probability"],
            ["int", "SleepMode", "task_min_time"],
            ["int", "Detect", "distance"],
            ["float", "WaitMode", "adaptive_loop_d"],
            ["float", "WaitMode", "adaptive_loop_limit"],
            ["float", "WaitMode", "task_probability"],
            ["int", "WaitMode", "task_min_time"],
        ]

        for check in check_list:
            import ast

            failed = 0
            # 3.1 check Form exists.
            if check[1] not in self.config.keys():
                self.error_msg = "no key \n" + check[1]
                failed = 1

            # 3.2 check value exists.
            elif check[2] not in self.config[check[1]].keys():
                self.error_msg = "no key \n" + check[1] + "\n" + check[2]
                failed = 2

            # 3.3 check value valid
            if failed == 0:
                try:
                    if check[0] == "int":
                        int(self.config[check[1]][check[2]])
                    elif check[0] == "float":
                        float(self.config[check[1]][check[2]])
                    elif check[0] == "list":
                        r = ast.literal_eval(self.config[check[1]][check[2]])
                        if type(r) is not list:
                            raise ValueError
                    elif check[0] == "bool":
                        r = ast.literal_eval(self.config[check[1]][check[2]])
                        if type(r) is not bool:
                            raise ValueError
                except Exception as E:
                    self.error_msg = "config error \n" + check[1] + "  \n" + check[2]
                    print(
                        "config error3 " + check[1] + "  " + check[2] + repr(E)
                    )
                    failed = 3

            # 3.4 if Form not exist
            if failed == 1:
                print("config error 1 " + check[1])
                self.config[check[1]] = {}
                self.config[check[1]][check[2]] = default_config[check[1]][check[2]]

            # 3.5 if value not exist [2]
            elif failed == 2:
                print("config error 2 " + check[1] + "  " + check[2])
                self.config[check[1]][check[2]] = default_config[check[1]][check[2]]

            # 3.6 if value not valid
            elif failed == 3:
                print("config error 2 " + check[1] + "  " + check[2])
                self.config[check[1]][check[2]] = default_config[check[1]][check[2]]

        return 0

    # [C.3] load hardware module
    def __load_hardware(self):
        if self.config is None:  # if config is not Loaded, cancel boot.
            return -1
        try:
            from modules.Hardware import v1

            self.hardware = v1.HardwareV1(self.config, self.base_path)
        except Exception as E:
            print("pino_init.__load_hardware(), " + repr(E))
            return -1
        else:
            return 0

    # [C.4] check internet connection
    def __load_internet(self):
        self.net_connected = False
        self.hardware.OLED.send_loading_console(step=2, msgs="check network..")
        a = time.time()
        http = PoolManager(
            timeout=Timeout(connect=1.0, read=2.0), retries=Retry(0, redirect=0)
        )
        try:
            response = http.request("HEAD", "https://status.cloud.google.com/")
            msg = "Internet.. " + str(response.status) + ".."
            self.hardware.OLED.send_loading_console(step=2, msgs=msg)
            if response.status == 200:  # if internet ok.
                print("Internet Not Connected")
                self.net_connected = True
                return 0
        except Exception as E:
            print(time.time() - a)
            print("pino_init.__load_internet(), " + repr(E))
            return -1
        else:
            return 0

    # [C.5] reset wifi, and try to re-connect 11 times
    def __reset_internet(self):
        # self.hardware.OLED.send_loading_console(step=3, msgs="\n Re connect..")

        # 1. try to reconnect max 10 times
        for i in range(11):
            # 2. wait 20 seconds to reconnect
            cnt = 0
            for j in range(20):
                time.sleep(1)
                cnt += 1
                if cnt % 2 == 0:
                    lcd_msg = "WiFi Re-connect. \n %d - %d times.." % (i, j)
                    self.hardware.OLED.send_loading_text(step=6, msg=lcd_msg)
                else:
                    lcd_msg = "WiFi Re-connect..\n %d - %d times.." % (i, j)
                    self.hardware.OLED.send_loading_text(step=7, msg=lcd_msg)

            self.__load_internet()
            # 5. if internet connected , close loop
            if self.net_connected is True:  # if network connected, break
                self.hardware.OLED.send_loading_console(step=8, msgs="OK")
                return 0
            # 6. if re connecti on failed over 11 times.
            elif i > 10:
                print("pino_init.__load_internet(), Wifi  not     found.. ")
                self.hardware.write(
                    text="wifi \n not found \n Shutdown", led=[255, 0, 100]
                )  # PURPLE LED ON
                return -1
            else:
                continue

    # [C.6] Cloud connect & check
    def __load_diaglogflow(self):
        # 1. if config is not Loaded, cancel boot.
        if self.config is None:
            return -1
        try:
            self.hardware.OLED.send_loading_console(step=9, msgs=".")
            from modules.Cloud.Google import pino_dialogflow

            self.cloud = pino_dialogflow.PinoDialogFlow(
                self.config["GCloud"]["google_project"],
                self.config["GCloud"]["language"],
                "/home/pi/Desktop/PinoBot/keys/" + self.config["GCloud"]["google_key"],
                int(self.config["GCloud"]["time_out"]),
            )
            self.hardware.OLED.send_loading_console(step=10, msgs=".")
            self.cloud.open_session()
            print("\n\n TEST Start!")
            self.hardware.OLED.send_loading_console(step=11, msgs=".")
            text_response = self.cloud.send_text("안녕하세요")

        except Exception as E:
            print("pino_init.__load_diaglogflow(), " + repr(E))
            return -1
        else:
            return 0

    # [D.1] config file reset
    def __config_default(self):
        config = configparser.ConfigParser()
        config["GCloud"] = {
            "google_key": "squarebot01-yauqxo-8d211b1f1a85.json",
            "google_project": "squarebot01-yauqxo",
            "language": "ko",
            "time_out": "7",
        }
        config["MOTOR"] = {
            "num_motor": "5",
            "motor_enable": "[1, 1, 1, 1, 1, 1, 1, 1]",
            "motor_min_angle": "[0, 0, 0, 0, 0, 0, 0, 0]",
            "motor_max_angle": "[170, 170, 170, 170, 170, 170, 170, 170]",
            "motor_default_angle": "[0, 0, 0, 0, 0, 0, 0, 0]",
        }
        config["LED"] = {"ON": "True"}
        config["OLED"] = {
            "console_font": "NanumSquareEB.ttf",
            "main_font": "NanumSquareEB.ttf",
        }
        config["GPIO"] = {"sonic_distance": "20", "sensor_timeout": "50"}
        config["UART"] = {"baud_rate": "115200"}

        config["SleepMode"] = {
            "state": "False",  #            # "Sleep_Mode" state, True or False
            "enter_limit_time": "60",  # sec        # how much time sensor detect object, change to "Sleep_Mode"
            "task_probability": "0.01",  #            # "Sleep_Mode_Task" in this random probability
            "task_min_time": "30",
        }  # sec        # minimum "Sleep_Mode_Task" duration

        config["Detect"] = {
            "distance": "30"
        }  # cm         # sonic sensor threshold to between 1 to 0

        config["WaitMode"] = {
            "adaptive_loop_d": "0.05",  # sec        # system loop wait time is adaptive, by this value
            "adaptive_loop_limit": "0.5",  # sec        # system loop wait time limit
            "task_probability": "0.01",  #            # "Wait_Mode_Task" in this random probability
            "task_min_time": "30",
        }  # sec        # minimum "Wait_Mode_Task" duration

        config["Boot"] = {"AutoBoot": "False"}

        return config
