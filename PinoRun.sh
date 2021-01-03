#! /bin/bash
cp -r -u /boot/PinoBot/PinoConfig.ini ~/Desktop/PinoBot/PinoConfig.ini  || prirntf " skip copy from /boot [1]"
cp -r -u /boot/PinoBot/keys ~/Desktop/PinoBot/keys || prirntf " skip copy from /boot [2]"
cp -r -u /boot/PinoBot/keys ~/Desktop/PinoBot/media || prirntf " skip copy from /boot [3]"
chmod 777 -R ~/Desktop/PinoBot/PinoConfig.ini || prirntf " skip chmod [1]"
chmod 777 -R ~/Desktop/PinoBot/keys || prirntf " skip skip chmod [2]"
chmod 777 -R ~/Desktop/PinoBot/media || prirntf " skip skip chmod [3]"
/usr/bin/python3 -u /home/pi/Desktop/PinoBot/pino_main.py &>> /dev/tty1 || /usr/bin/python3 -u /home/pi/Desktop/PinoBot/pino_main.py