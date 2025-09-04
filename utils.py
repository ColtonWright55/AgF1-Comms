import json
from collections import deque
import time

def recv_all(sock, n):
    # Helper function to receive exactly n bytes
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

def rcv_data(sock, on_status=None):
    while True:
        time.sleep(2.0)
        raw_msglen = recv_all(sock, 4)
        if not raw_msglen:
            print("Server closed connection")
            break

        msglen = int.from_bytes(raw_msglen, byteorder='big')

        msg = recv_all(sock, msglen)
        if not msg:
            print("Server closed connection")
            break

        try:
            print("Sleeping")
            time.sleep(2.00)
            data = json.loads(msg.decode('utf-8'))
            if on_status is not None:
                try:
                    on_status(data)
                except Exception:
                    pass
        except Exception as e:
            print("Error decoding JSON: ", e)
            break

def rcv_cmd(sock, on_status=None):
    while True:
        time.sleep(2.0)
        data = sock.recv(1024).decode('utf-8')
        if not data:
            print("ToolpathGen Socket closed")
            break
        print(data)



def send_commands(sock, commands):
    for cmd in commands:
        if cmd.strip():
            sock.sendall(cmd.encode('utf-8'))