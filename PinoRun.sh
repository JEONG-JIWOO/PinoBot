#! /bin/bash
chmod 777 -R /home/pi/Desktop/PinoBot/PinoConfig.ini || echo " skip chmod [1]"
chmod 777 -R /home/pi/Desktop/PinoBot/keys || echo " skip skip chmod [2]"
chmod 777 -R /home/pi/Desktop/PinoBot/media || echo " skip skip chmod [3]"
chmod 777  /home/pi/Desktop/PinoBot/main.log || echo " skip skip chmod [4]"
/usr/bin/python3 -u /home/pi/Desktop/PinoBot/pino_main.py &&echo " Launch PinoBot"