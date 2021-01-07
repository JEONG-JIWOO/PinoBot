#!/bin/bash
printf   "\n\n [step 1], update & upgrade rpi \n\n"

apt-get update -y
apt-get upgrade -y
yes | pip3 install --upgrade setuptools

printf   "\n\n [step 2], Install Driver"

cd /home/pi || { prirntf "cd /home/pi not fail"; exit 127;}
git clone https://github.com/PinoBot/seeed-voicecard_2020_1223
cd seeed-voicecard_2020_1223 || { prirntf "cd seeed-voicecard_2020_1223 fail "; exit 127;}
sudo ./install.sh
rm -rf /home/pi/seeed-voicecard_2020_1223 || { prirntf "remove seeed-voicecard_2020_1223 fail "; exit 127;}

printf   "\n\n [step 3], install apt packages \n\n"
apt-get -y install portaudio19-dev
apt-get -y install python3-dev

printf   "\n\n [step 4], copy source code "
mkdir -p /home/pi/Desktop || prirntf "Desktop exsists"
cp -r /boot/PinoBot/code/PinoBot  /home/pi/Desktop/PinoBot
chmod 777 -R /home/pi/Desktop/PinoBot

printf   "\n\n [step 5], install python modules \n\n"
yes | pip3 install -r /home/pi/Desktop/PinoBot/requirements.txt # why not run this. need check

printf "\n\n [step 6], add service"
cp /home/pi/Desktop/PinoBot/PinoBot.service /etc/systemd/system/PinoBot.service
systemctl enable PinoBot.service
systemctl start PinoBot.service

printf "\n\n [step 7] change passwd"
echo "pi:pinobot01" | chpasswd

for i in {10..0}
do
  printf   "\n [step 8], reboot in $i seconds"
  sleep 1
done

reboot