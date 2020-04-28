import configparser
import requests
import subprocess, time

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
        #  3. Check Network with Google
        response = requests.get('https://status.cloud.google.com/', timeout=2.50)
        if response.status_code == 200:  # if internet ok.
            print("Network Connected")
            pass
        else :
            #  3.2 Check wifi driver state.
            wpa_cli = subprocess.check_output('wpa_cli -V', shell=True).decode('utf-8')
            print(wpa_cli)

            if "Interactive" not in wpa_cli:
                #  3.2.1 , wpa_supplicant.conf error
                print("[E1] wpa_sup plicant.conf error")
                # self.hardware.write(text="[E1] wifi setting file is wrong")
                return -1

            else :
                # 3.2.2, wpa_supplicant.conf is fine
                # re-configure wifi
                subprocess.check_output('wpa_cli wlan0 reconfigure', shell=True).decode('utf-8')
                time.sleep(1)
                subprocess.check_output('wpa_cli scan', shell=True).decode('utf-8')
                print("Reset WIFI, wait for 10sec")
                time.sleep(10)

                response = requests.get('https://status.cloud.google.com/', timeout=2.50)
                if response.status_code != 200:  # if internet ok.
                    print("[E2] wifi not found, or password wrong")
                    return -1
                else :
                    print("Wifi re-connected,")


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