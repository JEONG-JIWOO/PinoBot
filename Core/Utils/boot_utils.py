import configparser
import requests
import subprocess, time
import logging
from logging.handlers import RotatingFileHandler
import sys
sys.path.append("/home/pi/Desktop/PinoBot/Core")

class BootLoader:
    """
    A. con & deconstruct
    """
    def __init__(self):
        # 0. Argument
        # 1. Static Variables

        self.base_path = "/home/pi/Desktop/PinoBot/"

        # 2. variables
        self.config_path = self.base_path+"/config.ini"  # TODO : change path to /boot partition
        self.net_connected = False
        self.error_msg =""

        # 3. Objects
        self.log = None
        self.config = None
        self.hardware = None
        self.cloud = None
        self.log = None

        # 4. Init Functions
        self.__set_config_default()
    def __del__(self):
        pass

    """
    B. Public Functions
    """
    # [B.1] Actual Function called from Outside.
    def run(self):
        # if boot Failed,
        if self.__main_boot() == -1:
            import sys
            sys.exit()

        # boot success
        return self.hardware , self.cloud

    """
    C. Private , Loading Functions
    """
    # [C.0] main boot Sequence
    def __main_boot(self):
        # 1. set logger
        self.__load_logger()

        # 2. load ini
        if self.__load_config() == -1:
            return -1

        # 2. check hardware valid
        if self.__load_hardware() == -1:
            return -1
        self.hardware.OLED.send_console(step=1, msgs="Hardware..OK.\n")

        # 3. check internet connected
        self.hardware.OLED.send_console(step=2, msgs="Internet..")
        self.__load_internet()

        # 3.1 if not, reset internet
        if not self.net_connected:
            self.__reset_internet()
        self.hardware.OLED.send_console(step=6, msgs="OK. \n")

        # 4. check dialogflow connection
        self.hardware.OLED.send_console(step=8, msgs="DialogFlow")
        if self.__load_diaglogflow() == -1:
            self.hardware.OLED.send_console(step=12, msgs="Fail. \n")
            time.sleep(1)
            self.hardware.OLED.send_console(step=12, msgs="Shutdown Robot")
            return -1
        self.hardware.OLED.send_console(step=13, msgs="OK. \n")

        # 5. copy media from /boot to media folder
        self.hardware.OLED.send_console(step=14, msgs="Copy Media..")
        if self.__media_copy() == -1:
            self.hardware.OLED.send_console(step=14, msgs="Fail. \n System Error!")
            time.sleep(1)
            self.hardware.OLED.send_console(step=14, msgs="Shutdown Robot.. \n")
        self.hardware.OLED.send_console(step=15, msgs="OK. \n")

        # 6. Finally all Check ok.
        self.hardware.OLED.send_console(step=16, msgs="Boot OK!")
        return 0

    # [C.1] log File load & check
    def __load_logger(self):
        # 1 set logger and formatter
        path = self.base_path + "/log/Boot.log"
        self.log = logging.getLogger("Boot")
        self.log.setLevel(logging.DEBUG)
        formatter = logging.Formatter('[%(levelname)s] (%(asctime)s : %(filename)s:%(lineno)d) > %(message)s')

        # 2 set file logger
        self.log_file = RotatingFileHandler(filename=path, maxBytes=5 * 1024 * 1024,
                                            mode='w',
                                            encoding='utf-8')
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
        if not os.path.isfile(self.config_path):
            self.__set_config_default()

        # 2. try to read config
        try:
            self.config = configparser.ConfigParser()
            self.config.read_file(open(self.config_path))
        except Exception as E:
            self.__set_config_default()
            self.error_msg = "can't read \n config file"
            self.log.error("boot_utils.__load_config(), " + repr(E))
            return -1

        #  3. check config value is VALID
        check_list= [['int', 'GCloud', 'time_out'],
                     ['int', 'MOTOR', 'num_motor'],
                     ['list', 'MOTOR', 'motor_enable'],
                     ['list', 'MOTOR', 'motor_min_angle'],
                     ['list', 'MOTOR', 'motor_max_angle'],
                     ['list', 'MOTOR', 'motor_default_angle'],
                     ['bool', 'LED', 'ON'],
                     ['int', 'GPIO', 'sonic_distance'],
                     ['int', 'GPIO', 'sensor_timeout'],
                     ['int', 'UART', 'baud_rate']]

        for check in check_list:
            import ast
            try:
                if check[0] == 'int':
                    int(self.config[check[1]][check[2]])
                elif check[0] == 'list':
                    ast.literal_eval(self.config[check[1]][check[2]])
                elif check[0] == 'bool':
                    ast.literal_eval(self.config[check[1]][check[2]])
            except Exception as E:
                self.error_msg = "config error \n\n"+  check[1] +"  \n\n" + check[2]
                break

        # 4. if config parsing Failed..
        # try to show error reason on OLED
        if self.error_msg != "":
            # noinspection PyBroadException
            try:
                from Core.Hardware.I2C.oled import OLED
                import board
                i2c = board.I2C()
                oled = OLED(i2c,
                            self.base_path,
                            'NanumSquareEB.ttf',
                            'NanumSquareEB.ttf')
                oled.send_console(step=1,msgs=self.error_msg)
            except:
                # event OLED FAILED
                pass
            return -1

        else:
            return 0

    # [C.3] load hardware
    def __load_hardware(self):
        if self.config is None:  # if config is not Loaded, cancel boot.
            return -1
        try:
            from Core.Hardware import v1
            self.hardware = v1.HardwareV1(self.config,self.base_path)
        except Exception as E:
            self.log.error("boot_utils.__load_hardware(), " + repr(E))
            return -1
        else:
            return 0

    # [C.4] check internet connection
    def __load_internet(self):
        try:
            response = requests.get('https://status.cloud.google.com/', timeout=2.50)
            if response.status_code != 200:  # if internet not ok.
                self.log.warning("Internet Not Connected")
                self.net_connected = False
            else:
                self.net_connected = True
        except Exception as E:
            self.log.error("boot_utils.__load_internet(), " + repr(E))
            return -1
        else:
            return 0

    # [C.5] reset wifi, and try to re-connect 5 times
    def __reset_internet(self):
        self.hardware.OLED.send_console(step=3, msgs="\n Re connect..")
        for i in range(6):
            msg = ""
            self.hardware.OLED.send_loading(step=4,msg="WiFi Reset.. \n")
            # 1. check wpa_supplicant.conf error
            try:
                self.log.warning("Checking WIFI..")
                msg = subprocess.check_output('sh ' + self.base_path + '/Core/Utils/wifiCheck.sh', shell=True).decode(
                    'utf-8')
            except Exception as E:
                #  3.1.1 , wpa_supplicant.conf error
                self.log.error("boot_utils.__load_internet(), Fail.. " + repr(E)+" "+ msg)
                self.hardware.write(text = "Fail Internet \n [E21],check wpa_supplicant \n Shutdown",led=[255, 0, 0])
                return -1  # Exit Program

            self.hardware.OLED.send_loading(step=5,msg="WiFi Reset.. OK \n WiFi re-connect..")
            # 2. wpa_supplicant.conf is fine,   re-set wifi
            try:  # Run WIFI reset scripts
                subprocess.check_output('sh ' + self.base_path + '/Core/Utils/wifiReset.sh', shell=True).decode('utf-8')
            except Exception as E:
                self.log.error("boot_utils.__load_internet(), Fail.. " + repr(E)+" "+ msg)
                self.hardware.write(text = "Fail Internet \n [E22],Linux Error \n Shutdown ",led=[255, 0, 0])
                return -1  # Exit Program

            # 3. wifi reset message
            self.log.warning("boot_utils.__Reset_internet(), reset wifi....")
            #self.hardware.write(led=[205, 140, 0])  # Orange LED on

            # 4. wait 30 seconds to reconnect
            cnt = 0
            for i in range(15):
                time.sleep(2)
                cnt += 1
                if cnt % 2 == 0:
                    self.hardware.OLED.send_loading(step=6,msg="WiFi Reset.. OK \n WiFi re-connect.")
                else:
                    self.hardware.OLED.send_loading(step=7,msg="WiFi Reset.. OK \n WiFi re-connect..")

            self.__load_internet()
            # 5. if internet connected , close loop
            if self.net_connected is True:  # if network connected, break
                self.hardware.send_console(step=8, msgs="OK")
                return 0
            elif i > 5:  # if re connection failed over 5 times.
                self.log.warning("boot_utils.__load_internet(), Wifi not found.. " )
                self.hardware.write(text= "wifi \n not found \n Shutdown",led=[255, 0, 100])  # PURPLE LED ON
                return -1

    # [C.6] Cloud connect & check Function
    def __load_diaglogflow(self):
        if self.config is None:  # if config is not Loaded, cancel boot.
            return -1
        try:
            self.hardware.OLED.send_console(step=9, msgs=".")
            from Core.Cloud.Google import pino_dialogflow
            self.cloud = pino_dialogflow.PinoDialogFlow(
                self.config['GCloud']['google_project'],
                self.config['GCloud']['language'],
                self.config['GCloud']['google_key'],
                int(self.config['GCloud']['time_out'])
            )
            self.hardware.OLED.send_console(step=10, msgs=".")
            self.cloud.open_session()
            print("\n\n TEST Start!")
            self.hardware.OLED.send_console(step=11, msgs=".")
            text_response = self.cloud.send_text("안녕하세요")
            self.log.info("Cloud test response %s" % text_response.query_result.query_text)

        except Exception as E:
            self.log.error("boot_utils.__load_diaglogflow(), " + repr(E))
            return -1
        else :
            return 0

    # [C.7] Copy Media files from /boot dir
    def __media_copy(self):
        import os , shutil
        # 1. check media folder exist.
        if not os.path.isdir(self.base_path+"/media"):  # if media folder not exist.
            try:
                os.mkdir(self.base_path+"/media")  # try to make media folder.
            except Exception as E: # if fail, write media message
                self.log.error(str(E))
                self.log.error("make media folder error")
                return -1

        # 2. copy media file.
        # TODO check works on wav and jpg/png files
        if os.path.isdir("/boot/media"):
            files = [ f for f in os.listdir('/boot/media/') if os.path.isfile(f) ]
            self.log.info("start copy media file")
            for file_name in files:
                if os.path.isfile(self.base_path+"/media/"+file_name):  # if file exist,
                    try:
                        os.remove(self.base_path+"/media/" + file_name) #  remove old file
                        shutil.copyfile("/boot/media/" + file_name, self.base_path + "/media/" + file_name)  # try copy
                    except Exception as E:
                        self.log.warning("boot_utils.__media_copy(), ( /boot/media/"
                                         + file_name + self.base_path + "/media/" + file_name + ") "+repr(E))
                else :
                    try :
                        shutil.copyfile("/boot/media/"+file_name,self.base_path+"/media/"+file_name) # try copy
                    except Exception as E:
                        self.log.warning("boot_utils.__media_copy(), copy fail " + file_name + ") " + repr(E))

        else :  # if no media file, pass
            self.log.info("skip copy media file")
            return 0

    #D.2 config file reset fuction
    def __set_config_default(self):
        config = configparser.ConfigParser()
        config['GCloud'] = {
                                'google_key':'/home/pi/Desktop/PinoBot/Keys/a2-bwogyf-c40e46d0dc2b.json',
                                'google_project':'a2-bwogyf',
                                'language': 'ko',
                                'time_out': '7'
                            }
        config['MOTOR'] ={
                                'num_motor':'5',
                                'motor_enable' : '[1, 1, 1, 1, 1, 1, 1, 1]',
                                'motor_min_angle' : '[0, 0, 0, 0, 0, 0, 0, 0]',
                                'motor_max_angle' : '[170, 170, 170, 170, 170, 170, 170, 170]',
                                'motor_default_angle' :  '[0, 0, 0, 0, 0, 0, 0, 0]',
        }
        config['LED'] = {
                                'ON' : 'True'
        }
        config['OLED'] ={
                                "console_font":'NanumSquareEB.ttf',
                                'main_font':'NanumSquareEB.ttf'
        }
        config['GPIO'] = {
                            'sonic_distance': '20',
                            'sensor_timeout': '50'
        }
        config['UART'] = {
                            'baud_rate': '115200'
        }

        with open(self.config_path,'w') as f:
            config.write(f)


"""
Test code. V1
"""
def test():
    d = BootLoader()
    #d
    d.run()
    print("tested")

if __name__ == '__main__':
    test()