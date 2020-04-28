#! /bin/sh
# when use windows, be careful for line saperator

ifconfig wlan0 down
rfkill unblock wifi
rfkill unblock all
ifconfig wlan0 up

wpa_cli -i wlan0 reconfigure

# To-do
# 1. http://www.troot.co.kr/wp/?p=1875
# 2. https://dgkim5360.tistory.com/entry/enable-wireless-network-using-systemd-networkd-on-arch-linux