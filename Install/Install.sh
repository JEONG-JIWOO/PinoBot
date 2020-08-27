#!/bin/bash
printf   "\n\n [step 1], update & upgrade rpi \n\n"

#apt-get update
#apt-get upgrade
python3 -m pip install --upgrade setuptools

printf   "\n\n [step 2], Install Driver"

git clone https://github.com/JEONG-JIWOO/seeed-voicecard
sudo bash ./seeed-voicecard/install.sh --compat-kernel
apt-get install portaudio19-dev

# port audio 설치 가이드라인인, 아래 패키지 설치하면 리스피커 모듈과 충돌.
#apt-get install libportaudio0 libportaudio2 libportaudiocpp0

printf   "\n\n [step 4], install python3-dev \n\n"
apt-get install python3-dev

printf   "\n\n [step 5], install pyaudio \n\n"
pip3 install pyaudio
pip3 install Pillow

printf   "\n\n [step 6], install dialogflow \n\n"
python3 -m pip install -r requirements.txt
pip3 install dialogflow

printf   "\n\n [step 7], install Hardware \n\n"
pip3 install RPi.GPIO
pip3 install adafruit-circuitpython-busdevice
pip3 install Adafruit-circuitpython-SSD1306
pip3 install adafruit-circuitpython-pca9685
pip3 install adafruit-circuitpython-motor

for i in {10..0}
do
  printf   "\n [step 8], reboot in $i seconds"
  sleep 1
done

reboot