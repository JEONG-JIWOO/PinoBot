import configparser
import requests
import subprocess, time
import tqdm

class BootLoader():
    def __init__(self):
        self.config_path = "/home/pi/PinoBot/config.ini"
        self.boot_log = None
        self.new_config = None

        self.hardware = None
        self.main()


    # 1. main boot loading process
    def main(self):
        #  1. BootUp

        #  2. Check Hardware
        self.load_hardware()

        #  3. Check Network with Google
        try:
            response = requests.get('https://status.cloud.google.com/', timeout=2.50)
            if response.status_code != 200:  # if internet not ok.
               raise NameError

        except:
            #  3.1 Check wifi driver state.
            try:
                wpa_cli = subprocess.check_output('wpa_cli -i wlan0 status', shell=True).decode('utf-8')
            except:
                #  3.1.1 , wpa_supplicant.conf error
                print("[E1] wpa_supp1licant.conf error")
                # self.hardware.write(text="[E1] wifi setting file is wrong")
                return -1
            else :
                # 3.1.2, wpa_supplicant.conf is fine  re-set wifi
                try:
                    subprocess.check_output(['sudo sh ./Core/Utils/wifiReset.sh'], shell=True).decode('utf-8')
                    print("reset wifi")
                    for i in tqdm.trange(30):
                        time.sleep(1)
                        # self.hardware.write(text="")

                    response = requests.get('https://status.cloud.google.com/', timeout=2.50)
                    if response.status_code != 200:  # if internet ok.
                        raise NameError
                except:
                    print("[E2] wifi name, password wrong")
                    # self.hardware.write(text="Reboot please")
                    return -1

        #  3.2. Network is connected
        print("Network Connected")
        self.config_read()

    def load_hardware(self):
        #from Core.Hardware import v1
        pass

    def load_cloud(self):
        #from Core.Cloud.google import pino_dialogflow
        pass


    def config_set_default(self):
        config = configparser.ConfigParser()

        config['GOOGLE CLOUD PROJECT'] = {'google_key':'squarebot01-yauqxo-149c5cb80866.json',
                                  'google_project':'squarebot01-yauqxo',
                                    'language': 'ko'
                            }
        config['MOTOR INDEX'] ={'number_of_motor':'3',
                                'index_list':'1,5,10'}

        with open(self.config_path,'w') as f:
            config.write(f)

    def config_read(self):
        """
        [WIP]
        read ini and save to object

        """
        self.new_config = None


    def get_file(self):
        # 1. import new config file. if exists

        # 2. import new key file if exsits.

        pass

def test():
    #from Core.Hardware import v1
    #from Core.Cloud.google import pino_dialogflow
    d = BootLoader()
    print("tested")


test()