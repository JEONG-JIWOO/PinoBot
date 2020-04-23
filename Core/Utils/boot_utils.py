import configparser


class BootUtils():
    def __init__(self,hardware):
        self.config_path = "/home/pi/PinoBot/config.ini"
        self.boot_log = None
        self.new_config = None
        self.boot_init(None,None)
        self.config_set_default()

    def boot_init(self,hardware,cloud):
        # 1. check new config exsists.
        self.config_read()

        if self.new_config is None :
            # there are no new setting, just do with traditional settings.

            # 1. check hardware
            self.hardware_check(hardware)

            # 2. check wifi.
            self.wifi_check()

            # 3. check cloud
            self.cloud_check(cloud)


        else :
            pass


    def config_set_default(self):
        config = configparser.ConfigParser()
        config['WIFI'] = {'wifi_id':'iot_4',
                          'wifi_password':'abcd1234'
                          }

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



    def wifi_new_connect(self):
        pass

    def wifi_check(self):
        pass

    def cloud_check(self, Cloud):
        pass

    def hardware_check(self, Hardware):
        pass

    def get_file(self):
        # 1. import new config file. if exists

        # 2. import new key file if exsits.

        pass

def test():
    from Core.Hardware import v1
    HardWare = v1.HardwareV1()

    d = BootUtils(HardWare)
    print("tested")

test()