import socket
import time
import sys

# tello drone ip and ports
DRONE_IP = "192.168.10.1"
CMD_PORT = 8889
LOCAL_PORT = 9000


def send_cmd(sock, cmd, address):
    # send command and check if drone says ok
    try:
        sock.sendto(cmd.encode(), address)
        response, _ = sock.recvfrom(1024)
        resp = response.decode().strip()
        print(f"[+] {cmd} -> {resp}")
        return resp == "ok"
    except socket.timeout:
        print(f"[-] {cmd} -> no response")
        return False


def main():
    # create socket and bind to local port to receive replies
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", LOCAL_PORT))
    sock.settimeout(5)
    address = (DRONE_IP, CMD_PORT)

    # first we have to enter sdk mode
    print("[*] entering sdk mode...")
    if not send_cmd(sock, "command", address):
        print("[-] cant reach drone, check wifi")
        sock.close()
        sys.exit(1)
    time.sleep(1)

    # turn on video stream
    print("[*] turning on video...")
    if not send_cmd(sock, "streamon", address):
        print("[-] stream failed")
        sock.close()
        sys.exit(1)

    print("[+] drone ready")
    print("[*] ctrl+c to land")

    # keep alive, tello drops connection after ~15s with no command
    try:
        while True:
            time.sleep(5)
            send_cmd(sock, "command", address)
    except KeyboardInterrupt:
        print("\n[*] landing...")
        send_cmd(sock, "land", address)

    sock.close()


if __name__ == "__main__":
    main()
