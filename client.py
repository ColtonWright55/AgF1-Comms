import socket
import json
import threading

HOST = '172.30.95.50' # The server's hostname or IP address
PORT = 12345 # The port used by the server

def recv_all(sock, n):
    # Helper function to receive exactly n bytes
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

def receive_data(socket):
    while True:
        # First receive 4 bytes length prefix
        raw_msglen = recv_all(s, 4)
        if not raw_msglen:
            print("Server closed connection")
            break

        msglen = int.from_bytes(raw_msglen, byteorder='big')

        # Receive the actual message
        msg = recv_all(s, msglen)
        if not msg:
            print("Server closed connection")
            break

        try:
            data = json.loads(msg.decode('utf-8'))
            print(f"Received data: {data}")
        except Exception as e:
            print("Error decoding JSON: ", e)
            break


def send_commands(socket):
    while True:
        cmd = input(">>> ")
        if cmd.strip():
            socket.sendall(cmd.encode('utf-8'))










with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print("Connected")

    threading.Thread(target=receive_data, args=(s,), daemon=True).start()

    send_commands(s)

    print("cjw Shutdown")