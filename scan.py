#!/usr/bin/env python3
import subprocess
import sys
import re
import argparse
import tempfile
import os


def check_root():
    if os.geteuid() != 0:
        print("[-] run as root: sudo python3 scan.py")
        sys.exit(1)


def check_dependencies():
    for cmd in ["airmon-ng", "airodump-ng"]:
        if subprocess.run(["which", cmd], capture_output=True).returncode != 0:
            print(f"[-] {cmd} not found, install aircrack-ng first")
            sys.exit(1)


def scan_networks(interface, band="bg", duration=15):
    # scan for nearby networks using airodump-ng
    print(f"[*] scanning on {interface} for {duration}s...")

    # create temp file for capture
    tmpdir = tempfile.mkdtemp()
    cap_prefix = os.path.join(tmpdir, "scan")

    cmd = [
        "airodump-ng",
        "--band", band,
        "-w", cap_prefix,
        "--output-format", "csv",
        interface
    ]

    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        proc.wait(timeout=duration)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()

    # read the csv output
    csv_file = cap_prefix + "-01.csv"
    if not os.path.exists(csv_file):
        # try without -01 suffix
        csv_file = cap_prefix + ".csv"

    if not os.path.exists(csv_file):
        print("[-] no scan results found")
        return []

    networks = parse_csv(csv_file)

    # cleanup
    for f in os.listdir(tmpdir):
        os.remove(os.path.join(tmpdir, f))
    os.rmdir(tmpdir)

    return networks


def parse_csv(csv_file):
    # parse airodump csv output
    networks = []
    try:
        with open(csv_file, "r") as f:
            content = f.read()

        # split by the AP section and station section
        lines = content.strip().split("\n")

        for line in lines:
            # look for lines with BSSID pattern (xx:xx:xx:xx:xx:xx)
            if re.search(r"([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}", line):
                parts = [p.strip() for p in line.split(",")]

                if len(parts) >= 14:
                    bssid = parts[0]
                    # skip empty or group BSSIDs
                    if not bssid or bssid == "(not associated)":
                        continue

                    power = parts[8] if parts[8] else "?"
                    channel = parts[3] if parts[3] else "?"
                    encryption = parts[5] if parts[5] else "?"
                    ssid = parts[13] if len(parts) > 13 else "(hidden)"

                    networks.append({
                        "bssid": bssid,
                        "ssid": ssid,
                        "channel": channel,
                        "power": power,
                        "encryption": encryption
                    })
    except Exception as e:
        print(f"[-] error parsing results: {e}")

    return networks


def find_drones(networks):
    # filter networks that look like drones
    drone_keywords = [
        "tello", "dji", "phantom", "mavic", "spark",
        "matrice", "inspire", "fpv", "mini", "air",
        "tel-", "dji-", "fpv-", "drone"
    ]

    drones = []
    for net in networks:
        ssid_lower = net["ssid"].lower()
        # check if ssid matches drone patterns
        if any(kw in ssid_lower for kw in drone_keywords):
            drones.append(net)
            continue
        # tello default SSID starts with TELLO-
        if ssid_lower.startswith("tello-"):
            drones.append(net)
            continue
        # open network with high signal could be drone
        if net["encryption"] == "OPN" and net["power"] != "?":
            try:
                if int(net["power"]) > -50:
                    drones.append(net)
            except ValueError:
                pass

    return drones


def print_results(networks, drones):
    if not networks:
        print("[-] no networks found")
        print("    try: make sure your adapter supports monitor mode")
        return

    print(f"\n[+] found {len(networks)} networks:\n")
    print(f"{'BSSID':<20} {'CH':<4} {'POWER':<7} {'ENC':<6} {'SSID'}")
    print("-" * 70)

    for net in networks:
        marker = " *" if net in drones else ""
        print(f"{net['bssid']:<20} {net['channel']:<4} {net['power']:<7} {net['encryption']:<6} {net['ssid']}{marker}")

    if drones:
        print(f"\n[+] possible drones (marked with *):\n")
        for d in drones:
            print(f"    BSSID:  {d['bssid']}")
            print(f"    SSID:   {d['ssid']}")
            print(f"    CH:     {d['channel']}")
            print(f"    POWER:  {d['power']} dBm")
            print()
        print("    copy the BSSID into run_attack.sh as DRONE_BSSID")
    else:
        print("\n[-] no obvious drones found")
        print("    if you know the drone's BSSID, add it to run_attack.sh manually")


def main():
    parser = argparse.ArgumentParser(description="scan for drone wifi networks")
    parser.add_argument("--interface", "-i", default="wlan0", help="wireless interface (default: wlan0)")
    parser.add_argument("--band", "-b", default="bg", choices=["a", "bg", "abg"], help="scan band (default: bg)")
    parser.add_argument("--duration", "-d", type=int, default=15, help="scan duration in seconds (default: 15)")
    args = parser.parse_args()

    check_root()
    check_dependencies()

    # put interface in monitor mode
    print(f"[*] enabling monitor mode on {args.interface}...")
    subprocess.run(["airmon-ng", "start", args.interface], capture_output=True)

    mon_iface = args.interface + "mon"
    # verify monitor interface exists
    result = subprocess.run(["ip", "link", "show", mon_iface], capture_output=True)
    if result.returncode != 0:
        print(f"[-] monitor interface {mon_iface} not found")
        print("    check: iwconfig")
        sys.exit(1)

    print(f"[+] monitor mode active: {mon_iface}")

    # scan
    networks = scan_networks(mon_iface, args.band, args.duration)

    # stop monitor mode
    print("[*] stopping monitor mode...")
    subprocess.run(["airmon-ng", "stop", mon_iface], capture_output=True)

    # find drones
    drones = find_drones(networks)

    # print results
    print_results(networks, drones)


if __name__ == "__main__":
    main()
