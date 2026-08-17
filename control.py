import socket
import time

# Drone Data
DRONE_IP = "192.168.10.1"
CMD_PORT = 8889

def send_commands():
    # UDP Socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2.0)
    server_address = (DRONE_IP, CMD_PORT)


    print("SDK connect")
    sock.sendto(b'command', server_address)
    time.sleep(1)

    print("Video Stream")
    sock.sendto(b'streamon', server_address)
    time.sleep(1)



    print("Land Command")
    sock.sendto(b'land', server_address)


    # print("Takeoff Command")
    # sock.sendto(b'takeoff', server_address)


    # print("Move Forward Command")
    # sock.sendto(b'forward 50', server_address)

    # sock.sendto(b'cw 90', server_address)
    sock.close()

if __name__ == "__main__":
    send_commands()
