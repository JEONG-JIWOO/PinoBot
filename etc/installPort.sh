# add service

cd /home/pi/Desktop/PinoBot
cp ./etc/redirectPort.service /etc/systemd/system/redirectPort.service
systemctl enable redirectPort.service
systemctl start redirectPort.service