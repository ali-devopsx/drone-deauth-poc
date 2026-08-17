# Drone Deauth & Takeover PoC

proof of concept project to demonstrate wireless deuthentecation attack and camera strem takeovere on tello drone

> Note: For authorized lab only


## project structure

* `run_attack.sh` - main bash script to handle network operations automaticaly
* `control.py` - python script to send SDK commands and start video

## requirements

* linux system (kali / ubuntu)
* aircrack-ng suite (`airmon-ng`, `aireplay-ng`)
* `nmcli` (NetworkManager)
* `ffmpeg` / `ffplay`
* python 3



## script details

### run_attack.sh
this bash script automate this process:

- enables monitor mode on the wireless card
- sends deauth packets to disconnect the target
- stops monitor mode and reconnects to drone wifi
- executes python control script in background
- opens `ffplay` to display live camera stram

### control.py
uses UDP sockets to communicate with tello SDK on port 8889:
- sends `command` to enable SDK mode
- sends `streamon` to enable camera broadcast
- includes land command for secuirty

## usage

make sure the script is executable and run with root privileges:

``` bash
ali@devops:~/drone-deauth-poc$ chmod +x run_attack.sh
ali@devops:~/drone-deauth-poc$ sudo ./run_attack.sh
