#! /bin/bash

# 80 port to 8080 port forward
sudo iptables -A PREROUTING -t nat -i eth0 -p tcp --dport 80 -j REDIRECT --to-port 8080
sudo iptables -A PREROUTING -t nat -i wlan0 -p tcp --dport 80 -j REDIRECT --to-port 8080

# save forward setting
sudo sh -c "iptables-save > /etc/iptables.rules"

# auto reload setting when boot
sudo apt-get install iptables-persistent

# install jupyter notebook
sudo apt-get install python3-matplotlib python3-scipy
sudo pip3 install jupyter
pip3 install --upgrade nbconvert ipython prompt_toolkit

# copy setting

