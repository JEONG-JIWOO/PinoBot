#!/usr/bin/python3

import configparser

# import requests
import subprocess, time
import logging
from logging.handlers import RotatingFileHandler
from urllib3 import PoolManager, Timeout, Retry


class Pino_Init:
    """
    A. con & deconstruct
    """

    def __init__(self, base_path):
        # 0. Argument
        # 1. Static Variables
        self.base_path = "/home/pi/Desktop/PinoBot/"  # base_path

        # 2. variables
        self.config_path = (
            "/home/pi/Desktop/PinoBot/PinoConfig.ini"  # self.base_path+"/config.ini"
        )
        self.net_connected = False
        self.error_msg = ""

        # 3. Objects
        self.log = None
        self.config = None
        self.hardware = None
        self.cloud = None

        # 4. Init Functions

    def __del__(self):
        try:
            self.log_file.close()
            self.log.removeHandler(self.log_file)
            self.log_consol.close()
            self.log.removeHandler(self.log_consol)
            del self.log

        except:
            pass

    """
    B. Public Functions
    """
    # [B.1] Actual Function called from Outside.
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
    # [C.0] main boot Sequence
    @property
    def __main_boot(self):
        # 1. set logger
        self.__load_logger()

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

        # 6. copy media from /home/pi/Desktop/ to media folder
        self.hardware.OLED.send_loading_console(step=14, msgs="Copy Media..pass")

        """
        not used for now.
        if self.__media_copy() == -1:
            self.hardware.OLED.send_loading_console(step=14, msgs="Fail. \n System Error!")
            time.sleep(1)
            self.hardware.OLED.send_loading_console(step=14, msgs="Shutdown Robot.. \n")
        """
        self.hardware.OLED.send_loading_console(step=15, msgs="OK. \n")

        # 7. Finally all Check ok.
        self.hardware.OLED.send_loading_console(step=16, msgs="Boot OK!")
        return 0

    # [C.1] log File load & check
    def __load_logger(self):
        # 1 set logger and formatter
        path = self.base_path + "log/Boot.log"
        self.log = logging.getLogger("Boot")
        self.log.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "[%(levelname)s] (%(asctime)s : %(filename)s:%(lineno)d) > %(message)s"
        )

        # 2 set file logger
        self.log_file = RotatingFileHandler(
            filename=path, maxBytes=5 * 1024 * 1024, mode="w", encoding="utf-8"
        )
        self.log_file.setFormatter(formatter)
        self.log.addHandler(self.log_file)

        # 3 set consol logger
        self.log_consol = logging.StreamHandler()
        self.log_consol.setFormatter(formatter)
        self.log.addHandler(self.log_consol)

        # 4 logger OK.
        self.log.info("Start BootLoader")
        return 0

    # [C.2] Config File load & check
    def __load_config(self):
        # 1. config not exist, write default config.
        import os

        default_config = self.__config_default()
        # if not os.path.isdir("/home/pi/Desktop/PinoBot"):
        #    self.error_msg = "no PinoBot \nfolder \n on /home/pi/Desktop/"
        #    self.log.error("no PinoBot \nfolder \n on /home/pi/Desktop/")
        #    return -1

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
            self.log.error("boot_utils.__load_config(), " + repr(E))
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
                    self.log.error(
                        "config error3 " + check[1] + "  " + check[2] + repr(E)
                    )
                    failed = 3

            # 3.4 if Form not exist
            if failed == 1:
                self.log.error("config error 1 " + check[1])
                self.config[check[1]] = {}
                self.config[check[1]][check[2]] = default_config[check[1]][check[2]]

            # 3.5 if value not exist [2]
            elif failed == 2:
                self.log.error("config error 2 " + check[1] + "  " + check[2])
                self.config[check[1]][check[2]] = default_config[check[1]][check[2]]

            # 3.6 if value not valid
            elif failed == 3:
                self.log.error("config error 2 " + check[1] + "  " + check[2])
                self.config[check[1]][check[2]] = default_config[check[1]][check[2]]

        return 0

    # [C.3] load hardware
    def __load_hardware(self):
        if self.config is None:  # if config is not Loaded, cancel boot.
            return -1
        try:
            from modules.Hardware import v1

            self.hardware = v1.HardwareV1(self.config, self.base_path)
        except Exception as E:
            self.log.error("boot_utils.__load_hardware(), " + repr(E))
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
                self.log.warning("Internet Not Connected")
                self.net_connected = True
                return 0
        except Exception as E:
            print(time.time() - a)
            self.log.error("boot_utils.__load_internet(), " + repr(E))
            return -1
        else:
            return 0

    # [C.5] reset wifi, and try to re-connect 5 times
    def __reset_internet(self):
        # self.hardware.OLED.send_loading_console(step=3, msgs="\n Re connect..")

        # 1. try to reconnect max 10 times
        for i in range(11):
            msg = ""

            # 2. check wpa_supplicant.conf error
            """
            self.hardware.OLED.send_loading_console(step=4, msgs="WiFi Reset.. \n")
            try:
                self.log.warning("Checking WIFI..")
                msg = subprocess.check_output('sh ' + self.base_path + '/Core/Utils/wifiCheck.sh', shell=True).decode(
                    'utf-8')
            except Exception as E:
                #  wpa_supplicant.conf error
                self.log.error("boot_utils.__load_internet(), Fail.. " + repr(E)+" "+ msg)
                self.hardware.write(text = "Fail Internet \n [E21],check wpa_supplicant \n Shutdown",led=[255, 0, 0])
                return -1  # Exit Program

            self.hardware.OLED.send_loading_console(step=5, msg="WiFi Reset.. OK \n WiFi re-connect..")
            # 3. wpa_supplicant.conf is fine,   re-set wifi
            try:  # Run WIFI reset scripts
                subprocess.check_output('sh ' + self.base_path + '/Core/Utils/wifiReset.sh', shell=True).decode('utf-8')
            except Exception as E:
                self.log.error("boot_utils.__load_internet(), Fail.. " + repr(E)+" "+ msg)
                self.hardware.write(text = "Fail Internet \n [E22],Linux Error \n Shutdown ",led=[255, 0, 0])
                return -1  # Exit Program

            self.log.warning("boot_utils.__Reset_internet(), reset wifi....")
            """
            self.hardware.write(led=[205, 140, 0])  # Orange LED on

            # 4. wait 20 seconds to reconnect
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
                self.log.warning("boot_utils.__load_internet(), Wifi  not     found.. ")
                self.hardware.write(
                    text="wifi \n not found \n Shutdown", led=[255, 0, 100]
                )  # PURPLE LED ON
                return -1
            else:
                continue

    # [C.6] Cloud connect & check Function
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
            self.log.info(
                "Cloud test response %s" % text_response.query_result.query_text
            )

        except Exception as E:
            self.log.error("boot_utils.__load_diaglogflow(), " + repr(E))
            return -1
        else:
            return 0

    # [C.7] Copy Media files from /home/pi/Desktop/ dir
    def __media_copy(self):
        import os, shutil

        # 1. check media folder exist.
        if not os.path.isdir(self.base_path + "/media"):  # if media folder not exist.
            try:
                os.mkdir(self.base_path + "/media")  # try to make media folder.
            except Exception as E:  # if fail, write media message
                self.log.error(str(E))
                self.log.error("make media folder error")
                return -1

        # 2. copy media file.
        # TODO check works on wav and jpg/png files
        if os.path.isdir("/home/pi/Desktop/media"):
            files = [
                f for f in os.listdir("/home/pi/Desktop/media/") if os.path.isfile(f)
            ]
            self.log.info("start copy media file")
            for file_name in files:
                if os.path.isfile(
                    self.base_path + "/media/" + file_name
                ):  # if file exist,
                    try:
                        os.remove(
                            self.base_path + "/media/" + file_name
                        )  #  remove old file
                        shutil.copyfile(
                            "/home/pi/Desktop/media/" + file_name,
                            self.base_path + "/media/" + file_name,
                        )  # try copy
                    except Exception as E:
                        self.log.warning(
                            "boot_utils.__media_copy(), ( /home/pi/Desktop/media/"
                            + file_name
                            + self.base_path
                            + "/media/"
                            + file_name
                            + ") "
                            + repr(E)
                        )
                else:
                    try:
                        shutil.copyfile(
                            "/home/pi/Desktop/media/" + file_name,
                            self.base_path + "/media/" + file_name,
                        )  # try copy
                    except Exception as E:
                        self.log.warning(
                            "boot_utils.__media_copy(), copy fail "
                            + file_name
                            + ") "
                            + repr(E)
                        )

        else:  # if no media file, pass
            self.log.info("skip copy media file")
            return 0

    # D.2 config file reset fuction
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
