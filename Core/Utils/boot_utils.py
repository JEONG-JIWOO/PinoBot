import configparser
import requests
import subprocess, time
import tqdm

class BootLoader():
    """
    [WIP]BOOT PROCESS
    1. parsing ini
    2. check hardware, i2c channel, and sonic sensor, if failed, show [HARDWARE ERROR]
    3. check wifi connection, if failed, try to connect 3 times and if failed, show [WIFI ERROR]
    4. check cloud connection, if failed, try to connect 3 times and if failed, show [CLOUD ERROR]
    5. if all completed. show [READY]" message
    6. start sensor thread

    """

    def __init__(self):
        self.base_path = "/home/pi/Desktop/PinoBot"
        self.config_path = self.base_path+"/config.ini"  # TODO : change path to /boot
        self.boot_log = None
        self.config = None

        self.hardware = None
        self.cloud = None


    def run(self):
        self.main()
        return self.hardware , self.cloud

    # 1. main boot loading process
    def main(self):
        #  1. BootUp

        #  2. Check Hardware
        self.load_hardware()

        #  3. Check Network with Google
        try:
            #raise NameError  # [TEST]
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
                self.hardware.write(led=[255, 0, 0]) # RED LED on
                return -1
            else :
                # 3.1.2, wpa_supplicant.conf is fine  re-set wifi
                try:
                    # Todo : Run script without sudo
                    subprocess.check_output('sudo sh '+self.base_path+'/Core/Utils/wifiReset.sh', shell=True).decode('utf-8')
                    print("reset wifi")
                    self.hardware.write_text_line1(text="WIFI RE-CONNECT")
                    self.hardware.write(led=[205, 140, 0])  # Orange LED on
                    cnt = 0
                    for i in tqdm.trange(15):
                        time.sleep(2)
                        cnt += 1
                        self.hardware.write_text_line2(text="=" * cnt)
                        if cnt % 2 ==0:
                            self.hardware.write(led=[205, 140, 0]) # Orange LED ON
                        else :
                            self.hardware.write(led=[30, 140, 0]) # GREEN LED ON

                except:
                    response = requests.get('https://status.cloud.google.com/', timeout=2.50)
                    if response.status_code != 200:  # if internet ok.
                        raise NameError

                    print("[E22] wifi name, password wrong")
                    self.hardware.write_text_line1(text="WIFI-ERROR")
                    self.hardware.write_text_line2(text="E22 NO-WIFI")
                    self.hardware.write(led=[255, 0, 100]) # PURPLE LED ON
                    return -1

        #  3.2. Network is connected
        print("Network OK!")
        self.hardware.write(text="Network OK!", led=[60, 60, 150], servo=[20, 70, 40])
        time.sleep(1)

        # 4. load Configure file
        self.load_config()

        # 5. load cloud.
        self.load_cloud()

        if self.cloud is not None and self.hardware is not None:
            print("Boot Finish")
            self.hardware.write(text="Boot FINISH",led=[0,0,0],servo=[90,90,90])

        time.sleep(2)
        return 0


    def load_hardware(self):
        from Core.Hardware import v1
        self.hardware = v1.HardwareV1()
        self.hardware.write(text="BootUp",led=[50,50,50],servo=[50,50,30])


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
        import os
        if not os.path.isfile(self.config_path):
            self.config_set_default()

        self.config_set_default()

        self.config = configparser.ConfigParser()
        self.config.read_file(open(self.config_path))

    def load_cloud(self):
        # TODO

        if self.config is None:
            return -1

        from Core.Cloud.Google import pino_dialogflow
        self.cloud = pino_dialogflow.PinoDialogFlow(
                                self.config['GOOGLE CLOUD PROJECT']['google_project'],
                                self.config['GOOGLE CLOUD PROJECT']['language'],
                                self.config['GOOGLE CLOUD PROJECT']['google_key'],
                                int(self.config['GOOGLE CLOUD PROJECT']['time_out'])
                                                    )
        self.cloud.open_session()

        print("\n\n TEST Start!")
        text_response = self.cloud.send_text("안녕하세요")
        print("[Q] : %s " % text_response.query_result.query_text)
        print("[A] : accuracy:%0.3f | %s " % (
                                              text_response.query_result.intent_detection_confidence,
                                              text_response.query_result.fulfillment_text
                                              ))
        print("Cloud is Fine")


    def config_set_default(self):
        config = configparser.ConfigParser()

        config['GOOGLE CLOUD PROJECT'] = {
                                'google_key':'/home/pi/Desktop/PinoBot/Keys/a2-bwogyf-c40e46d0dc2b.json',
                                'google_project':'a2-bwogyf',
                                'language': 'ko',
                                'time_out':'7'
                            }
        config['MOTOR INDEX'] ={
                                'number_of_motor':'3',
                                'index_list':'1,5,10'
        }

        with open(self.config_path,'w') as f:
            config.write(f)

def test():
    d = BootLoader()
    d.run()
    print("tested")
