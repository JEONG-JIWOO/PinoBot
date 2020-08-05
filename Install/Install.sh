#!/bin/bash
# http://wiki.seeedstudio.com/ReSpeaker_4_Mic_Array_for_Raspberry_Pi/

echo -e "/n/n [step 1.1], update & upgrade rpi /n/n"

sudo apt-get update
sudo apt-get upgrade

echo -e "/n/n [step 1.2], download driver source"

git clone https://github.com/respeaker/seeed-voicecard

echo -e "/n/n [step 1.3], Install"

sudo ./seeed-voicecard/install.sh


echo -e "/n/n [step 2.1], install portAudio19 /n/n"

# port audio 설치 가이드라인인, 아래 패키지 설치하면 리스피커 모듈과 충돌.
#sudo apt-get install libportaudio0 libportaudio2 libportaudiocpp0 
sudo apt-get install portaudio19-dev

echo -e "/n/n [step 2.2], install python3-dev /n/n"
sudo apt-get install python3-dev

echo -e "/n/n [step 2.3], install pyaudio /n/n"
pip3 install pyaudio

echo -e "/n/n [step 3], install dialogflow /n/n"
python3 -m pip install --upgrade setuptools
python3 -m pip install -r requirements.txt
pip3 install dialogflow

echo -e "/n/n [step 4], reboot in 2 seconds"
sleep 1
echo -e "/n/n [step 4], reboot in 1 seconds"
sleep 1

reboot