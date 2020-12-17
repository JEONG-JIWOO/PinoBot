#!/bin/bash
printf   "\n\n [step 1], update & upgrade rpi \n\n"

#apt-get update
#apt-get upgrade
python3 -m pip install --yes --upgrade setuptools

printf   "\n\n [step 2], Install Driver"

git clone https://github.com/respeaker/seeed-voicecard
cd seeed-voicecard
sudo ./install.sh
apt-get --yes install portaudio19-dev

printf   "\n\n [step 3], install python3-dev \n\n"
apt-get --yes install python3-dev

printf "\n\n [step 4], remove seeed-voicecard"
rm -rf /home/pi/seeed-voicecard

printf   "\n\n [step 5], cp source_code "
mkdir -p /home/pi/Desktop
cp -r /boot/PinoBot/code/PinoBot  /home/pi/Desktop/PinoBot
chmod 777 -R  /home/pi/Desktop/PinoBot

printf   "\n\n [step 6], install python modules \n\n"
pip3 install -r /home/pi/Desktop/PinoBot/requirements.txt

printf "\n\n [step 7], add service"
cp /home/pi/Desktop/PinoBot/PinoBot.service /etc/systemd/system/PinoBot.service
systemctl enable PinoBot.service
systemctl start PinoBot.service

printf "\n\n [step 8] change passwd"
echo "pi:pinobot01" | chpasswd

for i in {10..0}
do
  printf   "\n [step 9], reboot in $i seconds"
  sleep 1
done

reboot