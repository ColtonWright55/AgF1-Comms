# Written for Python 2.7.6

import sys
import time
import datetime
import numpy as np
import socket
import linuxcnc
import json
import struct

HOST = '172.30.95.50'
PORT = 12345

# Connect to linuxcnc status channel
try:
    Ls = linuxcnc.stat()
except linuxcnc.error as detail:
    print("Error:", detail)
    sys.exit(1)

# Fields we will be sending over ethernet to client
fields = ['actual_position', 'command']

sample_rate = 0.5
sample_interval = 1.0 / sample_rate

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.bind((HOST, PORT))
    s.listen(1)

    conn, addr = s.accept()
    try:
        print "Connected by", addr

        while True:
            Ls.poll()
            data = {field: getattr(Ls, field) for field in fields}
            data['timestamp'] = datetime.datetime.now().isoformat()
            message = json.dumps(data)
            message_bytes = message.encode('utf-8')  # Python 2: encode to bytes

            conn.sendall(struct.pack('!I', len(message_bytes)))
            conn.sendall(message_bytes)

            time.sleep(sample_interval)
    finally:
        conn.close()
finally:
    s.close()