import configparser
import requests
import subprocess, time
import logging
from logging.handlers import RotatingFileHandler
import sys
sys.path.append("/home/pi/Desktop/PinoBot/Core")

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

        net_status = 0

        # 2. Check Hardware
        try:
            self._load_hardware()
            self.log.info("Hardware init success")
        except :
            self.log.error("Hardware init Fail")
            return -1

        self.hardware.write_text_line1(text="Version 0_9_01")
        time.sleep(3)
        self.hardware.write_text_line1(text="")

        # 3. Check Network with Google
        try:
            response = requests.get('https://status.cloud.google.com/', timeout=2.50)
            if response.status_code != 200:  # if internet not ok.
                self.log.warning("Internet Not Connected")
                net_status = -1
            else :
                net_status =1
        except:
            net_status = -1

        for i in range(6): # try reconnect 5 times.
            if  net_status > 0:  # if network connected, break
                break
            elif net_status <= -6: # if re connection failed over 5 times.
                self.log.error("Internet Not Connected")
                self.log.error("[E23] wifi name, password wrong")
                self.hardware.write_text_line1(text="WIFI-ERROR")
                self.hardware.write_text_line2(text="E22 NO-WIFI")
                self.hardware.write(led=[255, 0, 100])  # PURPLE LED ON
                return -1

            msg =""
            try:
                self.log.warning("Checking WIFI..")
                msg = subprocess.check_output('sh '+self.base_path+'/Core/Utils/wifiCheck.sh', shell=True).decode('utf-8')
            except Exception as E:
                #  3.1.1 , wpa_supplicant.conf error
                self.log.error(msg)
                self.log.error(str(E))
                self.log.error("[E21] wpa_supp1licant.conf error")
                self.hardware.write_text_line1(text="BOOT-ERROR")
                self.hardware.write_text_line2(text="E21 WIFI-WRONG")
                self.hardware.write(led=[255, 0, 0]) # RED LED on
                return -1  # Exit Program

            #  3.2 wpa_supplicant.conf is fine  re-set wifi
            try:  # Run WIFI reset scripts
                subprocess.check_output('sh '+self.base_path+'/Core/Utils/wifiReset.sh', shell=True).decode('utf-8')
            except Exception as E:
                self.log.error(str(E))
                self.log.error("[E22] Wifi Reconnect error")
                self.hardware.write_text_line1(text="BOOT-ERROR")
                self.hardware.write_text_line2(text="E22 WIFI-RECONNECT")
                self.hardware.write(led=[255, 0, 0])  # RED LED on
                return -1  # Exit Program

            self.log.warning("Reset wifi....")
            self.hardware.write_text_line1(text="WIFI RECONNECT-"+str(-net_status))
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

            # 3.3 Check google cloud connection again
            try:
                response = requests.get('https://status.cloud.google.com/', timeout=2.50)
            except :  # 3.3.1 if error occur
                net_status -= 1
            else :    # 3.3.2 No error, but not connected,
                if response.status_code != 200:  # check status code.
                    net_status -= 1
                else: # 3.3.3 Connected!
                    net_status = 1

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
            self.log.warning("Media folder copy error")

        # 8. if boot Final Check ok.
        if self.cloud is not None and self.hardware is not None:
            self.log.info("Boot Finish")
            self.hardware.write(text="Boot FINISH",led=[0,0,0],servo=[90,90,90])
            time.sleep(2)
            return 0
        else :
            self.log.error("Final error")
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
        except Exception as E:
            self.log.error(str(E))
            self.log.error("Hardware init error")
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
            self.log.error("Load config file Fail, reset config file to Default")
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
            self.log.error(str(E))
            self._set_config_default()
            self.log.error("Cloud Init Fail, reset config file to Default")
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
                self.log.error(str(E))
                self.log.error("make media folder error")
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

if __name__ == '__main__':
    test()