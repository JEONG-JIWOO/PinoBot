import configparser
import requests
import subprocess, time
import logging
from logging.handlers import RotatingFileHandler

class BootLoader():
    """

    """

    """
    A.1 Initializing Boot Loader Object
    """
    def __init__(self):
        self.base_path = "/home/pi/Desktop/PinoBot"
        self.config_path = self.base_path+"/config.ini"  # TODO : change path to /boot partition
        self.log = None
        self.config = None
        self.hardware = None
        self.cloud = None
        self.log = None

    """
    B.1 run Fuction called from Outside.
    """
    def run(self):
        if self._boot_main() == -1:
            import sys
            sys.exit()
        return self.hardware , self.cloud

    """
    B.2 Main boot loading process
    """
    def _boot_main(self):
        # 1. initializing logger
        self._set_logger(self.base_path+"/log/Boot.log")

        # 2. Check Hardware
        try:
            self._load_hardware()
            self.log.info("Hardware init success")
        except :
            self.log.Error("Hardware init Fail")
            return -1

        # 3. Check Network with Google
        try:
            #raise NameError  # [TEST]
            response = requests.get('https://status.cloud.google.com/', timeout=2.50)
            if response.status_code != 200:  # if internet not ok.
                self.log.warning("Internet Not Connected")
                raise NameError

        except:
            # 3.1 Check wifi driver state.
            msg =""
            try:
                # Todo : Run script without sudo
                self.log.warning("Checking WIFI..")
                msg = subprocess.check_output('sudo sh '+self.base_path+'/Core/Utils/wifiCheck.sh', shell=True).decode('utf-8')
            except Exception as E:
                #  3.1.1 , wpa_supplicant.conf error
                self.log.Error(msg)
                self.log.Error(E)
                self.log.Error("[E21] wpa_supp1licant.conf error")
                self.hardware.write_text_line1(text="BOOT-ERROR")
                self.hardware.write_text_line2(text="E21 WIFI-SET-WRONG")
                self.hardware.write(led=[255, 0, 0]) # RED LED on
                return -1  # Exit Program

            #  3.2 wpa_supplicant.conf is fine  re-set wifi
            try:
                # Run WIFI reset scripts      Todo : Run script without sudo
                subprocess.check_output('sudo sh '+self.base_path+'/Core/Utils/wifiReset.sh', shell=True).decode('utf-8')
                self.log.warning("Reset wifi....")
                self.hardware.write_text_line1(text="WIFI RE-CONNECT")
                self.hardware.write(led=[205, 140, 0])  # Orange LED on

                cnt = 0  # wait 30 seconds to reconnect
                for i in range(15):
                    time.sleep(2)
                    cnt += 1
                    self.hardware.write_text_line2(text="=" * cnt)
                    if cnt % 2 ==0:
                        self.hardware.write(led=[205, 140, 0]) # Orange LED ON
                    else :
                        self.hardware.write(led=[30, 140, 0]) # GREEN LED ON
            except Exception as E:
                self.log.Error(E)
                self.log.Error("[E22] Wifi Reconnect Error")
                self.hardware.write_text_line1(text="BOOT-ERROR")
                self.hardware.write_text_line2(text="E22 WIFI-RECONNECT")
                self.hardware.write(led=[255, 0, 0])  # RED LED on
                return -1  # Exit Program

            # 3.3 Check google cloud connection agaiun
            finally:
                response = requests.get('https://status.cloud.google.com/', timeout=2.50)
                if response.status_code != 200:  # if internet Not ok.
                    self.log.Error("Internet Not Connected")
                    self.log.Error("[E23] wifi name, password wrong")
                    self.hardware.write_text_line1(text="WIFI-ERROR")
                    self.hardware.write_text_line2(text="E22 NO-WIFI")
                    self.hardware.write(led=[255, 0, 100]) # PURPLE LED ON
                    return -1  # Exit Program

        # 4. Network is connected
        self.log.info("Network OK!")
        self.hardware.write(text="Network OK!", led=[60, 60, 150], servo=[20, 70, 40])
        time.sleep(1)

        # 5. load Configure file
        if self._load_config() == -1:
            self.hardware.write_text_line1(text="Set File ERROR")
            self.hardware.write_text_line2(text="E31 Wrong Config")
            self.hardware.write(led=[240, 0, 0], servo=[90, 90, 90])
            time.sleep(2)
            return -1

        # 6. load cloud.
        if self._load_cloud() == -1:
            self.hardware.write_text_line1(text="Set File ERROR")
            self.hardware.write_text_line2(text="E31 Wrong Config")
            self.hardware.write(led=[240, 0, 0], servo=[90, 90, 90])
            time.sleep(2)
            return -1

        # 7. Copy Media file
        if self._boot_copy() == -1:
            self.log.warning("Media folder copy Error")

        # 8. if boot Final Check ok.
        if self.cloud is not None and self.hardware is not None:
            self.log.info("Boot Finish")
            self.hardware.write(text="Boot FINISH",led=[0,0,0],servo=[90,90,90])
            time.sleep(2)
            return 0
        else :
            self.log.Error("Final Error")
            return -1

    """
    C.1 Hardware load & check Function
    """
    def _load_hardware(self):
        # TODO :  Use, i2cdetect, and parse answer, detect i2c state.
        """
        try:
            i2c = subprocess.check_output('i2cdetct -y 1', shell=True).decode('utf-8')
        except:
            print("[E10] hardware ERROR")
        """
        try:
            from Hardware import v1
            self.hardware = v1.HardwareV1()
            self.hardware.write(text="BootUp",led=[50,50,50],servo=[50,50,30])
        except Exception as E :
            self.log.Error("Hardware init Error")
            self.log.Error(E)
            return -1
        else :
            return 0

    """
    C.2 Config File load & check Function
    """
    def _load_config(self):
        import os
        if not os.path.isfile(self.config_path):
            self._set_config_default()

        try:
            self.config = configparser.ConfigParser()
            self.config.read_file(open(self.config_path))
            int(self.config['GOOGLE CLOUD PROJECT']['time_out'])
            int(self.config['SENSOR']['sonic_distance'])
            int(self.config['SENSOR']['sensor_timeout'])
        except :
            self._set_config_default()
            self.log.Error("Load config file Fail, reset config file to Default")
            return -1
        else :
            return 0

    """
    C.3 Cloud connect & check Function
    """
    def _load_cloud(self):
        if self.config is None: # if config is not Loaded, cancel boot.
            return -1

        try:
            from Cloud.Google import pino_dialogflow
            self.cloud = pino_dialogflow.PinoDialogFlow(
                                    self.config['GOOGLE CLOUD PROJECT']['google_project'],
                                    self.config['GOOGLE CLOUD PROJECT']['language'],
                                    self.config['GOOGLE CLOUD PROJECT']['google_key'],
                                    int(self.config['GOOGLE CLOUD PROJECT']['time_out'])
                                                        )
            self.cloud.open_session()

            print("\n\n TEST Start!")
            text_response = self.cloud.send_text("안녕하세요")
            self.log.info("Cloud test response %s"%text_response.query_result.query_text)

        except Exception as E:
            self._set_config_default()
            self.log.Error("Cloud Init Fail, reset config file to Default")
            return -1

    """
    D.1 logger initialize fuction 
    """
    def _set_logger(self,path):
        # 2.1 set logger and formatter
        self.log = logging.getLogger("Boot")
        self.log.setLevel(logging.DEBUG)
        formatter = logging.Formatter('[%(levelname)s] (%(asctime)s : %(filename)s:%(lineno)d) > %(message)s')

        # 2.2 set file logger
        self.log_file = RotatingFileHandler(filename = path, maxBytes=5*1024*1024,
                                            mode='w',
                                            encoding='utf-8')
        self.log_file.setFormatter(formatter)
        self.log.addHandler(self.log_file)

        # 2.3 set consol logger
        self.log_consol = logging.StreamHandler()
        self.log_consol.setFormatter(formatter)
        self.log.addHandler(self.log_consol)

        # 2.4 logger Done.
        self.log.info("Start DialogFlow Module")

    """
    D.2 config file reset fuction
    """
    def _set_config_default(self):
        config = configparser.ConfigParser()

        config['GOOGLE CLOUD PROJECT'] = {
                                'google_key':'/home/pi/Desktop/PinoBot/Keys/a2-bwogyf-c40e46d0dc2b.json',
                                'google_project':'a2-bwogyf',
                                'language': 'ko',
                                'time_out': '7'
                            }
        config['MOTOR INDEX'] ={
                                'number_of_motor':'3',
                                'index_list':'1,5,10'
        }
        config['SENSOR'] = {
                            'sonic_distance': '20',
                            'sensor_timeout': '50'
        }

        with open(self.config_path,'w') as f:
            config.write(f)

    """
    D.3 copy media file fuction
    """
    def _boot_copy(self):
        import os , shutil

        # 1. check media folder exsist.
        if not os.path.isdir(self.base_path+"/media"):  # if media folder not exist.
            try:
                os.mkdir(self.base_path+"/media")  # try to make media folder.
            except Exception as E: # if fail, write media message
                self.log.Error("make media folder error")
                self.log.Error("E")
                return -1

        # 2. copy media file.
        if os.path.isdir("/boot/media"):
            files = [ f for f in os.listdir('/boot/media/') if os.path.isfile(f) ]
            self.log.info("start copy media file")
            for file in files:
                if os.path.isfile(self.base_path+"/media/"+file):  # if file exist,
                    try:
                        os.remove(self.base_path+"/media/" + file) #  remove old file
                        shutil.copyfile("/boot/media/" + file, self.base_path + "/media/" + file)  # try copy
                    except:
                        self.log.warning("%s delete ,copy fail "%(self.base_path+"/media/" + file))
                else :
                    try :
                        shutil.copyfile("/boot/media/"+file,self.base_path+"/media/"+file) # try copy
                    except :
                        self.log.warning("%s copy fail "%("/boot/media/"+file))

        else :  # if no media file, pass
            self.log.info("skip copy media file")
            return 0


"""
Test code. V1
"""
def test():
    d = BootLoader()
    d.run()
    print("tested")
