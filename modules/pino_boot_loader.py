#!/usr/bin/python3
"""
Description : PinoBot Dialogflow handling module
Author : Jiwoo Jeong
Email  : Jiwoo@gepetto.io  / jjw951215@gmail.com

V 1.0
    - make module comment

"""
import time , configparser

class PinoBootLoader:
    def __init__(self, base_path, log):
        # 0. Argument
        # 1. Static Variables
        self.base_path = base_path

        # 2. variables
        self.config_path = self.base_path +"/settings/pino_config.ini"
        self.net_connected = False

        # 3. Objects
        self.config = None
        self.hardware = None
        self.cloud = None
        self.log = log

    """
    B. Public Functions
    """
    # [B.1] Actual Function called from outside.
    def boot(self):
        """
        Description
        -----------
            boot function call from outside

        Notes
        -----
            only this function is called in outside class
            if error occurs during boot, exit program

        Return
        ------
            self.hardware  : hardware object
            self.cloud     : pino_dialogflow object
            self.config    : config parser

        """

        # if boot Failed,
        self.log.info("pino_boot_loader.py: start boot")
        loding_str = (
            "     @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@      \n"
            "     @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@      \n"
            "     @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@      \n"
            "     @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@--@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@      \n"
            "     @@@@@@@@@@@@@@@@@@@@@@@@@@@@ ---:@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@      \n"
            "     @@@@@@@@@@@@@@@@@@@@@@@@@@@----~::@@@@@@@@@@@@@@@@@@@@@@@@@@@@@      \n"
            "     @@@@@@@@@@@@@@@@@@@@@@@@@@,--,,-~:@@@@@@@@@@@@@@@@@@@@@@@@@@@@@      \n"
            "     @@@@@@@@@@@@@@@@@@@@@@@@@--,,,.,~:@@@@@::---@@@@@@@@@@@@@@@@@@@      \n"
            "     @@@@@@@@@@@@@@@@@@@@@@@@@--,...,~:@@@@:~~---@@@@@@@@@@@@@@@@@@@      \n"
            "     @@@@@@@@@@@@@@@@@@@@@@@@----,,,,~:@@@:~-----@@@@@@@@@@@@@@@@@@@      \n"
            "     @@@@@@@@@@@@@@@@@@@@@@@------,,,~:@@@:~,,,---@@@@@@@@@@@@@@@@@@      \n"
            "     @@@@@@@@@@@@@@@@@@@@@@@-----,---~~@@:~-.,,,--@@@@@@@@@@@@@@@@@@      \n"
            "     @@@@@@@@@@@@@@@@@@@@@@----,...,,,,..~-~-,,,--@@@@@@@@@@@@@@@@@@      \n"
            "     @@@@@@@@@@@@@@@@@@@@@@---,...........--~,,---@@@@@@@@@@@@@@@@@@      \n"
            "     @@@@@@@@@@@@@@@@  ....---.............-~-,---@@@@@@@@@@@@@@@@@@      \n"
            "     @@@@@@@@@@@@@@@@,,....~-,.....~!~.......,----@@@@@@@@@@@@@@@@@@      \n"
            "     @@@@@@@@@@@@@@@@--,,,.@-......:$:.~-... ..--- @@@@@@@@@@@@@@@@@      \n"
            "     @@@@@@@@@@@@@@@..---,,:@.......,..;~......---@@@@@@@@@@@@@@@@@@      \n"
            "     @@@@@@@@@@@@@@-,.@@--~--.   . ,---,.......---@@@@@@@@@@@@@@@@@@      \n"
            "     @@@@@@@@@@@@@@--. ::~----.   .,---,......,---@@@@@@@@@@@@@@@@@@      \n"
            "     @@@@@@@@@@@@@@--...,~,..--....,---,......--- @@@@@@@@@@@@@@@@@@      \n"
            "     @@@@@@@@@@@@@@@-----,...,. .  ,---,..,--...@@@@@@@@@@@@@@@@@@@@      \n"
            "     @@@@@@@@@@@@@@@@@@:~----,..-.........,..@,. @@@@@@@@@@@@@@@@@@@      \n"
            "     @@@@@@@@@@@@@@@@@@@@---,...,-,.... ..-.,:-..,@@@@@@@@@@@@@@@@@@      \n"
            "     @@@@@@@@@@@@@@@@@@@@@--,...,,.....,-~~,~:-...@@@@@@@@@@@@@@@@@@      \n"
            "     @@@@@@@@@@@@@@@@@@@@@@@@...,. ,-. .,,~:::-...@@@@@@@@@@@@@@@@@@      \n"
            "     @@@@@@@@@@@@@@@@@@@@@@@@@@-.  :$:  .,,~---...@@@@@@@@@@@@@@@@@@      \n"
            "     @@@@@@@@@@@@@@@@@@@@@@@@@@@   ~!~  ...,----@@@@@@@@@@@@@@@@@@@@      \n"
            "     @@@@@@@@@@@@@@@@@@@@@@@@@@@..     ....,----@@@@@@@@@@@@@@@@@@@@      \n"
            "     @@@@@@@@@@@@@@@@@@@@@@@@@@;-, ,~, ,,..,---@@@@@@@@@@@@@@@@@@@@@      \n"
            "     @@@@@@@@@@@@@@@@@@@@@@@@@@--, :$: ,-..,--@@@@@@@@@@@@@@@@@@@@@@      \n"
            "     @@@@@@@@@@@@@@@@@@@@@@@@@@--,.-:-.,--@@@@@@@@@@@@@@@@@@@@@@@@@@      \n"
            "     @@@@@@@@@@@@@@@@@@@@@@@@@,,--,...,,,,,@@@@@@@@@@@@@@@@@@@@@@@@@      \n"
            "     @@@@@@@@@@@@@@@@@@@@@@@@@,,---,,,,,,,,@@@@@@@@@@@@@@@@@@@@@@@@@      \n"
            "     @@@@@@@@@@@@@@@@@@@@@@@@@,,,--,,,,,,,,@@@@@@@@@@@@@@@@@@@@@@@@@      \n"
            "     @@@@@@@@@@@@@@@@@@@@@@@@...............@@@@@@@@@@@@@@@@@@@@@@@@      \n"
            "     @@@@@@@@@@@@@@@@@@@@@@@@...         ...@@@@@@@@@@@@@@@@@@@@@@@@      \n"
            "     @@@@@@@@@@@@@@@@@@@@@@@@...         ...@@@@@@@@@@@@@@@@@@@@@@@@      \n"
            "     @@@@@@@@@@@@@@@@@@@@@@@@ ..         ...@@@@@@@@@@@@@@@@@@@@@@@@      \n"
            "     @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@      \n"
            "     @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@      \n"
            "     @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@      \n"
            "   _   _        _  _         ______  _               ______         _     \n"
            "  | | | |      | || |        | ___ \(_)              | ___ \       | |    \n"
            "  | |_| |  ___ | || |  ___   | |_/ / _  _ __    ___  | |_/ /  ___  | |_   \n"
            "  |  _  | / _ \| || | / _ \  |  __/ | || '_ \  / _ \ | ___ \ / _ \ | __|  \n"
            "  | | | ||  __/| || || (_) | | |    | || | | || (_) || |_/ /| (_) || |_   \n"
            "  \_| |_/ \___||_||_| \___/  \_|    |_||_| |_| \___/ \____/  \___/  \__|  \n\n"
            "==========================================================================\n"
            "  Launch PinoBot Manager...\n"
            "==========================================================================\n"
        )
        print(loding_str)

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
        """
        Description
        -----------
            boot sequence
            1. load config file
            2. check hardware valid
            3. check internet connected
            4. if not, reset internet
            5. check dialogflow connection

        Return
        ------
            result    0 success
                     -1 fail

        """
        # 1. load config file
        if self.__load_config() == -1:
            self._load_hardware()
            self.hardware.display_console(1,"Config File \n Error\n")
            return -1
        self.log.info("pino_boot_loader.py: config.. Complete")

        # 2. check hardware valid
        if self._load_hardware() == -1:
            return -1
        self.log.info("pino_boot_loader.py: hardware.. Complete")
        self.hardware.display_console(5,'Hardware.. done\n')

        # 3. check internet connected
        if self._load_internet() == -1:
            pass

        # 4. if not, reset internet
        if not self.net_connected:
            self.hardware.display_console(6, 'Internet.. reset\n')
            self._reset_internet()
        self.log.info("pino_boot_loader.py: internet.. Complete")
        self.hardware.display_console(9, 'Internet.. done\n')

        # 5. check dialogflow connection
        self.hardware.display_console(12, 'Dialogflow')
        if self._load_diaglogflow() == -1:
            self.hardware.display_console(1, 'Fail!')
            time.sleep(1)
            return -1
        self.hardware.display_console(15, ' done\n')

        return 0

    # [C.2]
    def __load_config(self):
        """
        Description
        -----------
            boot sequence 1.
            Config File load & check

        Notes
        -----
            1. check config file,
                if not exist make default one
            2. read config file
                if failed, shutdown boot sequence
            3. check config value is valid
                3.1 check Form  exists.     -> fail_case 1
                3.2 check value exists.     -> fail_case 2
                3.3 check value valid.      -> fail_case 3

            4. if failed, restore to default value

        Return
        ------
        result    0 success
                 -1 fail

        [TODO] : Use configparser.get() method make logic more simple

        """

        # 1. if config not exist, write default config.
        import os , configparser
        default_config = self._config_default()
        if not os.path.isfile(self.config_path):
            self.log.warning("pino_boot_loader.py: config.. Not exist, set to Default ")
            with open(self.config_path, "w") as configfile:
                default_config.write(configfile)

        # 2. try to read config
        try:
            self.config = configparser.ConfigParser()
            with open(self.config_path) as f:
                self.config.read_file(f)
        except Exception as E:
            self._config_default()
            self.log.error("pino_boot_loader.py: config.. Fail | "+ repr(E))
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

        for c_v in check_list:
            import ast

            fail_case = 0
            # 3.1 check Form exists.
            if c_v[1] not in self.config.keys():
                self.log.warning("pino_boot_loader.py: config.. NO key | " + c_v[1])
                fail_case = 1

            # 3.2 check value exists.
            elif c_v[2] not in self.config[c_v[1]].keys():
                self.log.warning("pino_boot_loader.py: config.. NO key | "+ c_v[1] + "\n" + c_v[2])
                fail_case = 2

            # 3.3 check value valid
            else:
                try:
                    if c_v[0] == "int":
                        int(self.config[c_v[1]][c_v[2]])
                    elif c_v[0] == "float":
                        float(self.config[c_v[1]][c_v[2]])
                    elif c_v[0] == "list":
                        r = ast.literal_eval(self.config[c_v[1]][c_v[2]])
                        if type(r) is not list:
                            raise ValueError
                    elif c_v[0] == "bool":
                        r = ast.literal_eval(self.config[c_v[1]][c_v[2]])
                        if type(r) is not bool:
                            raise ValueError
                except Exception as E:
                    self.log.warning("pino_boot_loader.py: config.. Value error | "+ c_v[1] + "  " + c_v[2] + repr(E))

            # 4. if config has value error, Restore to default value
            if fail_case == 1:
                print("config error 1 " + c_v[1])
                self.config[c_v[1]] = {}
                self.config[c_v[1]][c_v[2]] = default_config[c_v[1]][c_v[2]]

            elif fail_case == 2:
                print("config error 2 " + c_v[1] + "  " + c_v[2])
                self.config[c_v[1]][c_v[2]] = default_config[c_v[1]][c_v[2]]

            elif fail_case == 3:
                print("config error 2 " + c_v[1] + "  " + c_v[2])
                self.config[c_v[1]][c_v[2]] = default_config[c_v[1]][c_v[2]]

        return 0

    def _load_hardware(self):
        """
        Description
        -----------
            boot sequence 2.
            load hardware module

        Return
        ------
        result    0 success
                 -1 fail

        """

        try:
            from modules.Hardware import v1
            self.hardware = v1.Hardware(self.config, self.base_path,self.log)

            console_log = ""
            failed_module = 0
            if self.hardware.state['OLED']:
                for module_name, inited in self.hardware.state.items():
                    if not inited :
                        console_log += module_name + " "
                        failed_module +=1
            if failed_module == 0:
                self.hardware.display_console(4," 6/6 module inited\n")
            else :
                console_log = console_log +"\m %d/6 module inited\n"%(6-failed_module)
                self.hardware.display_console(4, console_log)

        except Exception as E:
            self.log.error("pino_boot_loader.py: _load_hardware(), " + repr(E))
            return -1
        else:
            return 0

    def _load_internet(self):
        """
        Description
        -----------
            boot sequence 3.
            check internet connection

        Notes
        -----
            use urllib3 to set connection timeout manually and reduce check time

        Return
        ------
        result    0 success
                 -1 fail

        """

        self.net_connected = False
        try:
            from urllib3 import PoolManager, Timeout , Retry
            http = PoolManager(
                timeout=Timeout(connect=1.0, read=2.0), retries=Retry(0, redirect=0)
            )
            response = http.request("HEAD", "https://status.cloud.google.com/")
            if response.status == 200:  # if internet ok.
                self.log.info("pino_boot_loader.py: internet not connected!")
                self.net_connected = True
        except Exception as E:
            self.log.error("pino_boot_loader.py: _load_internet(), " + repr(E))
            return -1
        else:
            return 0

    def _reset_internet(self):
        """
        Description
        -----------
            boot sequence 4.
            wait for reconnect internet

        Notes
        -----
            wait for 11 loop,
            each loop is 5sec,

        Return
        ------
        result    0 success
                 -1 fail

        [TODO] : ADD wifi reset shell Scripts

        """

        self.hardware.display_console(6, 'reconnect..')
        for i in range(11):
            self.log.warning("pino_boot_loader.py: try to Reconnect internet %d times.."%i)
            for j in range(5):
                time.sleep(1)
                if i % 2 == 0:
                    self.hardware.display_console(7, '')
                if i % 2 == 1:
                    self.hardware.display_console(8, '')

                self._load_internet()
                if self.net_connected is True:  # if network connected, break
                    return 0

        self.log.error("pino_boot_loader.py: internet not connected!")
        return -1

    # [C.6] Cloud connect & check
    def _load_diaglogflow(self):
        """
        Description
        -----------
            boot sequence 5.
            Dialogflow connect


        Return
        ------
        result    0 success
                 -1 fail

         [TODO] : change config access method to config parser.get()

        """
        if self.config is None:
            return -1
        from modules.Cloud.Google import pino_dialogflow
        self.hardware.display_console(13, '.')

        self.cloud = pino_dialogflow.PinoDialogFlow(
            self.config["GCloud"]["google_project"],
            self.config["GCloud"]["language"],
            self.base_path+"/keys/" + self.config["GCloud"]["google_key"],
            int(self.config["GCloud"]["time_out"]),
            self.log
        )
        self.hardware.display_console(14, '.')
        self.cloud.open_session()
        self.cloud.send_text("안녕하세요")
        if self.cloud.gcloud_state > 0 :
            return 0
        else :
            return -1



    @staticmethod
    def _config_default():
        """
        Description
        -----------
            return HARD-CODDED default config value

        Return
        ------
            configparser.ConfigParser() object

        """
        config = configparser.ConfigParser()
        config["GCloud"] = {
            "google_key": "",
            "google_project": "",
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
