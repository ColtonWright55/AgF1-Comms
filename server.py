# Written for Python 2.7.6

import sys
import time
import datetime
import numpy as np
import socket
import linuxcnc
import json
import struct
import threading

HOST = '172.30.95.50'
PORT = 12345

def handle_client(conn):
    def send_data():
        while True:
            Ls.poll()

            data = {field: getattr(Ls, field) for field in fields}
            data['timestamp'] = datetime.datetime.now().isoformat()

            message = json.dumps(data)
            message_bytes = message.encode('utf-8')  # Python 2: encode to bytes

            conn.sendall(struct.pack('!I', len(message_bytes)))
            conn.sendall(message_bytes)

            time.sleep(sample_interval)

    def receive_commands():
        while True:
            cmd = conn.recv(1024)
            print "received command: ", cmd


    threading.Thread(target=send_data, daemon=True).start()
    receive_commands()



# Connect to linuxcnc status channel
try:
    Ls = linuxcnc.stat()
except linuxcnc.error as detail:
    print("Error:", detail)
    sys.exit(1)




# Fields we will be sending over ethernet to client
fields = ['actual_position', 'command']

sample_rate = 50
sample_interval = 1.0 / sample_rate





s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.bind((HOST, PORT))
    s.listen(1)
    try:
        conn, addr = s.accept()
        print "Connected by", addr

        handle_client(conn)
    finally:
        conn.close()
finally:
    s.close()