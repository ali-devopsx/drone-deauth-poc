# bugs i found and fixed

## control.py

- socket was never bound to a local port -> couldnt receive drone replies
  fixed: added `sock.bind(("", 9000))`
- land command was sent right after streamon -> drone lands immediately
  fixed: removed land, only send it on ctrl+c now
- no check if drone actually responded to commands
  fixed: send_cmd() checks for "ok" reply
- no keepalive -> tello disconnects after ~15s
  fixed: send "command" every 5s in a loop

## run_attack.sh

- monitor interface name was hardcoded as wlan0mon
  fixed: auto detect with ip link show
- no airmon-ng check kill -> other processes block monitor mode
  fixed: added check kill at start
- no NetworkManager restart after stopping monitor mode
  fixed: added systemctl restart
- no check if drone is reachable after reconnect
  fixed: added ping check
- variables were not quoted ($INTERFACE instead of "$INTERFACE")
  fixed: quoted all variables
- no config validation -> script ran with placeholder MAC
  fixed: added check at start
- no set -e -> script continued after errors
  fixed: added set -e
- no cleanup trap -> wifi card stuck in monitor mode on failure
  fixed: added trap cleanup EXIT

## other

- ffplay had wrong params, caused high latency
  fixed: changed to `-probesize 32 -framerate 30`
- empty run-deauth.sh file deleted
- run-deauth.sh was empty, deleted it

## before running

- change DRONE_BSSID and DRONE_SSID to match your drone
- run: nmcli dev wifi list (while connected to drone)
- make sure you have aircrack-ng, ffplay, python3 installed
- run with sudo
