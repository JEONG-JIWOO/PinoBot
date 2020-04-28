#! /bin/sh

MYID=$1
MYPW=$2
echo id=$MYID
echo pw=$MYPW
wpa_cli -p /var/run/wpa_supplicant terminate
ifconfig wlan0 down
rm -rf /var/run/wpa_supplicant
wpa_supplicant2 -p /var/run/wpa_supplicant -iwlan0 -Dwext -c ./wpa.conf -B
ifconfig wlan0 up
#sleep 5
wpa_cli -p /var/run/wpa_supplicant remove_network 0
wpa_cli -p /var/run/wpa_supplicant ap_scan 1
#wpa_cli -p /var/run/wpa_supplicant scan
#wpa_cli -p /var/run/wpa_supplicant scan_results
wpa_cli -p /var/run/wpa_supplicant add_network
wpa_cli -p /var/run/wpa_supplicant set_network 0 ssid "\"$MYID\""
wpa_cli -p /var/run/wpa_supplicant set_network 0 psk "\"$MYPW\""
wpa_cli -p /var/run/wpa_supplicant select_network 0
sleep 1
for a in 1 2 3
do
        MTEMP=`wpa_cli -p /var/run/wpa_supplicant status | sed -n 's/wpa_state=//pg'`
        echo status = $MTEMP

        if [ "$MTEMP" = "COMPLETED" ]
        then
                echo "Connect!"
                exit 0
        else
                echo try $a retry
                sleep 1
        fi
done

if [ $a -eq 3 ]
then
        echo :"Fail to Connect"
        exit 1
fi
