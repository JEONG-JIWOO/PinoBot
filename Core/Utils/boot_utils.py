import configparser
import requests
import subprocess, time
import tqdm

class BootLoader():
    def __init__(self):
        self.base_path = "/home/pi/Desktop/PinoBot"
        self.config_path = self.base_path+"/config.ini"
        self.boot_log = None
        self.new_config = None

        self.hardware = None
        self.cloud = None


    def open(self):
        self.main()
        return self.hardware , self.cloud

    # 1. main boot loading process
    def main(self):
        #  1. BootUp

        #  2. Check Hardware
        self.load_hardware()

        #  3. Check Network with Google
        try:
            raise NameError  # [TEST]

            response = requests.get('https://status.cloud.google.com/', timeout=2.50)
            if response.status_code != 200:  # if internet not ok.
               raise NameError

        except:
            #  3.1 Check wifi driver state.
            a =""
            try:
                # Todo : Run script without sudo
                 a = subprocess.check_output('sudo sh '+self.base_path+'/Core/Utils/wifiCheck.sh', shell=True).decode('utf-8')
            except:
                #  3.1.1 , wpa_supplicant.conf error
                print(a)
                print("[E21] wpa_supp1licant.conf error")
                self.hardware.write_text_line1(text="BOOT-ERROR")
                self.hardware.write_text_line2(text="E21 WIFI-SET-WRONG")
                return -1
            else :
                # 3.1.2, wpa_supplicant.conf is fine  re-set wifi
                try:
                    # Todo : Run script without sudo
                    subprocess.check_output('sudo sh '+self.base_path+'/Core/Utils/wifiReset.sh', shell=True).decode('utf-8')
                    print("reset wifi")
                    self.hardware.write_text_line1(text="WIFI RE-CONNECT")
                    cnt = 0
                    for i in tqdm.trange(15):
                        time.sleep(2)
                        cnt += 1
                        self.hardware.write_text_line2(text="=" * cnt)
                except:
                    response = requests.get('https://status.cloud.google.com/', timeout=2.50)
                    if response.status_code != 200:  # if internet ok.
                        raise NameError

                    print("[E22] wifi name, password wrong")
                    self.hardware.write_text_line1(text="WIFI-ERROR")
                    self.hardware.write_text_line2(text="E22 NO-WIFI")
                    return -1

        #  3.2. Network is connected
        print("Network OK!")
        self.hardware.write(text="Network OK!")

        # 4. load Configure file
        self.load_config()

        # 5. load cloud.
        self.load_cloud()
        time.sleep(5)
        return 0


    def load_hardware(self):
        from Core.Hardware import v1
        self.hardware = v1.HardwareV1()

        # TODO
        """
        Use, i2cdetect, and parse answer, detect i2c state.
        try:
            i2c = subprocess.check_output('i2cdetct -y 1', shell=True).decode('utf-8')
        except:
            print("[E10] hardware ERROR")
        """
        return 0

    def load_config(self):
        # TODO

        pass

    def load_cloud(self):
        # TODO
        from Core.Cloud.Google import pino_dialogflow

        pass



    def config_set_default(self):
        config = configparser.ConfigParser()

        config['GOOGLE CLOUD PROJECT'] = {'google_key':'squarebot01-yauqxo-149c5cb80866.json',
                                  'google_project':'squarebot01-yauqxo',
                                    'language': 'ko',
                                    'time_out':'7'
                            }
        config['MOTOR INDEX'] ={'number_of_motor':'3',
                                'index_list':'1,5,10'}

        with open(self.config_path,'w') as f:
            config.write(f)

def test():
    d = BootLoader()
    d.open()
    print("tested")


test()