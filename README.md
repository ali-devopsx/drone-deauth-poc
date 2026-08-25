# Drone Deauth & Takeover PoC

proof of concept for deauthenticating a DJI Tello drone's controller and taking over via SDK commands + video stream.

> for authorized lab testing only

## how it works

1. `scan.py` scans nearby wifi networks and finds the drone
2. `run_attack.sh` puts wireless card in monitor mode and sends deauth packets
3. controller/phone gets disconnected from drone wifi
4. script reconnects to drone wifi and sends SDK commands via `control.py`
5. video stream opens in ffplay

## project structure

```
├── run_attack.sh      # main script - deauth + reconnect + control
├── control.py         # SDK commands over UDP (port 8889)
├── scan.py            # network scanner - find drone bssid
├── install.sh         # install all dependencies
├── INCIDENT.md        # bugs i found and fixed
└── README.md
```

## requirements

- linux with wireless adapter that supports monitor mode
- aircrack-ng suite (airmon-ng, aireplay-ng, airodump-ng)
- NetworkManager (nmcli)
- ffmpeg / ffplay
- python 3

## quick start

```bash
# install dependencies
chmod +x install.sh
sudo ./install.sh

# find your drone
sudo python3 scan.py

# edit run_attack.sh and set DRONE_BSSID + DRONE_SSID

# run the attack
sudo ./run_attack.sh
```

## scan.py

scans for nearby wifi networks and identifies potential drones:

```bash
sudo python3 scan.py
sudo python3 scan.py --interface wlan0    # use specific adapter
sudo python3 scan.py --band abg           # scan all bands
```

## control.py

sends SDK commands to tello over UDP:

- `command` - enter SDK mode
- `streamon` - start H.264 video stream on port 11111
- `land` - land the drone (on ctrl+c)
- keeps connection alive with heartbeat every 5s

## how the deauth works

the tello drone creates its own wifi network (like a hotspot). your phone/controller connects to it. the deauth attack:

1. puts your wifi card in monitor mode
2. sends deauth frames to the drone's BSSID
3. this disconnects all clients (your phone)
4. you reconnect before the phone does
5. now you control the drone via SDK

## troubleshooting

- **monitor interface not found**: check `iwconfig`, your card might need a different driver
- **cant reach drone**: make sure you're connected to drone wifi, try `ping 192.168.10.1`
- **no video stream**: check firewall, try `ffplay -probesize 32 -framerate 30 -i udp://@:11111`
- **deauth not working**: make sure you're close enough to the drone, try continuous deauth with `--deauth 0`
