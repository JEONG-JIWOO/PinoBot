#!/bin/bash
printf   "\n\n [step 1], update & upgrade rpi \n\n"

apt-get update -y
apt-get upgrade -y
yes | pip3 install --upgrade setuptools

printf   "\n\n [step 2], Install Driver"
git clone https://github.com/HinTak/seeed-voicecard #HinTak's repository is more stable than official
cd ./seeed-voicecard || { prirntf "cd seeed-voicecard fail "; exit 127;}
sudo bash ./install.sh || { prirntf "\n\n cd seeed-voicecard install fail , try install use --compat-kernel" ; sudo bash ./install.sh --compat-kernel ;}
cd ..
rm -rf ./seeed-voicecard || { prirntf "remove seeed-voicecard fail "; exit 127;}

printf   "\n\n [step 3], install apt packages \n\n"
apt-get -y install portaudio19-dev
apt-get -y install python3-dev

printf   "\n\n [step 4], install python modules \n\n"
yes | pip3 install -r ./requirements.txt # why not run this. need check

printf "\n\n [step 5], add service"
cp ./PinoBot.service /etc/systemd/system/PinoBot.service
systemctl enable PinoBot.service
systemctl start PinoBot.service

printf "\n\n [step 6], Copy PinoSet to /boot"

cp -r ./PinoSet /boot

printf "\n\n [step 7] change passwd"
#echo "pi:pinobot01" | chpasswd

printf "\n\n [step 8] copy .asoundrc file "
#cp .asoundrc /home/pi/.asoundrc

for i in {10..0}
do
  printf   "\n [step 9], reboot in $i seconds"
  sleep 1
done

reboot