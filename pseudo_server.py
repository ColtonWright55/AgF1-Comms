# Written for Python 2.7.6
# See if sending random numbers also crashes the server instead of constant linuxcnc polling

import sys
import time
import datetime
import numpy as np
import socket
import json
import struct
import threading

HOST = '172.30.95.50'
PORT = 12345

def handle_client(conn):
    def send_data():
        while True:

            data = {}
            data['timestamp'] = datetime.datetime.now().isoformat()
            data['command'] = ""
            data['actual_position'] = np.random.random(9).tolist()

            message = json.dumps(data)
            message_bytes = message.encode('utf-8')  # Python 2: encode to bytes
            try:
                conn.sendall(struct.pack('!I', len(message_bytes)))
                conn.sendall(message_bytes)
            except socket.error as e:
                print "Send failed", e

            time.sleep(sample_interval)

    def receive_commands():
        while True:
            cmd = conn.recv(1024)
            print "received command: ", cmd


    t = threading.Thread(target=send_data)
    t.daemon = True
    t.start()
    receive_commands()



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
        print("Connected by", addr)

        handle_client(conn)
    finally:
        conn.close()
finally:
    s.close()