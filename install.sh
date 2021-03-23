#! /bin/bash

###################################
# Check install condition
###################################

# Check if run in root
if [ "$EUID" -ne 0 ]
then
  echo "ERROR: Run with sudo command"
  exit
fi

# Check if username is pi
if [ "$SUDO_USER" != "pi" ]
then
  echo "ERROR: Run in username 'pi'"
  exit
fi

# Check if run default directory
DEFAULT_DIR="/home/pi/Desktop/PinoBot"
CURRENT_DIR=$(pwd)
if [ "$CURRENT_DIR" != "$DEFAULT_DIR" ]
then
  echo "Copy files to default directory"
  # Copy all files to default directory
  mkdir -p /home/pi2/Desktop/PinoBot
  cp -r "$CURRENT_DIR"* "$DEFAULT_DIR"

  # Move execution to default directory
  cd $DEFAULT_DIR
fi

###################################
# Install Pinobot requirement
###################################
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
sudo apt-get install iptables-persistent
sudo apt-get install python3-matplotlib python3-scipy

printf   "\n\n [step 4], install python modules \n\n"
yes | pip3 install -r ./etc/requirements.txt
yes | pip3 install --upgrade nbconvert ipython prompt_toolkit

###################################
# Install jupyter notebook
###################################
# Change host name
#RANDOM_FRONT=$(printf %03d $(( $RANDOM % 1000 )))
#RANDOM_BACK=$(printf %04d $(( $RANDOM % 10000 )))
#NEW_HOST_NAME="p$RANDOM_FRONT$RANDOM_BACK"
#hostnamectl set-hostname $NEW_HOST_NAME
#sudo hostname $NEW_HOST_NAME

# auto reload package install

printf   "\n\n [step 5], setting jupyter \n\n"
# 80 port to 8080 port forward
sudo iptables -A PREROUTING -t nat -i eth0 -p tcp --dport 80 -j REDIRECT --to-port 8080
sudo iptables -A PREROUTING -t nat -i wlan0 -p tcp --dport 80 -j REDIRECT --to-port 8080

# save forward setting to reload on boot
sudo netfilter-persistent save

# copy setting
mkdir -p /home/pi/.jupyter/
cp ./settings/jupyter_notebook_config.py /home/pi/.jupyter/jupyter_notebook_config.py

# grant execute permissions
chown pi:pi "$DEFAULT_DIR" -R
chown pi:pi /home/pi/.jupyter -R
chmod +x ./etc/runJupyter.sh

# add service
cp ./etc/jupyter.service /etc/systemd/system/jupyter.service
systemctl enable jupyter.service
systemctl start jupyter.service

# reboot
for i in {5..0}
do
  printf   "\n reboot in $i seconds"
  sleep 1
done
reboot