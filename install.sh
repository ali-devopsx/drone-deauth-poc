#!/bin/bash
set -e

# install dependencies for drone-deauth-poc
# run with sudo: sudo ./install.sh

if [ "$EUID" -ne 0 ]; then
  echo "[-] run as root: sudo ./install.sh"
  exit 1
fi

echo "[*] updating package list..."
apt update -qq

echo "[*] installing aircrack-ng..."
apt install -y aircrack-ng

echo "[*] installing ffmpeg..."
apt install -y ffmpeg

echo "[*] installing networkmanager..."
apt install -y network-manager

echo "[*] installing python3..."
apt install -y python3 python3-pip

echo "[*] checking wireless adapter..."
if ip link show wlan0 &>/dev/null; then
  echo "[+] found wlan0"
else
  echo "[-] no wlan0 found, check: iwconfig"
fi

echo "[*] checking monitor mode support..."
if airmon-ng 2>/dev/null | grep -q "wlan"; then
  echo "[+] monitor mode supported"
else
  echo "[-] monitor mode may not work, check your adapter"
fi

echo ""
echo "[+] done! all dependencies installed"
echo "[*] next steps:"
echo "    1. sudo python3 scan.py          # find your drone"
echo "    2. edit run_attack.sh            # set DRONE_BSSID + DRONE_SSID"
echo "    3. sudo ./run_attack.sh          # run the attack"
