#! /bin/sh
# when use windows, be careful for line saperator

ifconfig wlan0 down
rfkill unblock wifi
rfkill unblock all
ifconfig wlan0 up

wpa_cli -i wlan0 reconfigure

# sudo visudo
# %pi   ALL=(root) NOPASSWD: /sbin/ifconfig wlan0 up
# %pi   ALL=(root) NOPASSWD: /sbin/ifconfig wlan0 down
# pi ALL=NOPASSWD: /usr/sbin/rfikill,/sbin/wpa_cli
# To-do
# 1. http://www.troot.co.kr/wp/?p=1875
