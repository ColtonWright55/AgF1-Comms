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
            s = Ls.poll()
            for x in dir(Ls):
                if not x.startswith("_"):
                    # print(x, getattr(Ls,x))
                    pass # 

            data = {field: getattr(Ls, field) for field in fields}
            data['timestamp'] = datetime.datetime.now().isoformat()

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

            if ok_for_mdi() and cmd is not None:
                Lc.mode(linuxcnc.MODE_MDI)
                Lc.wait_complete() # wait until mode switch executed
                print "Sending Lc.mdi(cmd)"
                Lc.mdi(cmd)

    t = threading.Thread(target=send_data)
    t.daemon = True
    t.start()
    receive_commands()

def ok_for_mdi():
    Ls.poll()
    return not Ls.estop and Ls.enabled and (Ls.interp_state == linuxcnc.INTERP_IDLE)






# Connect to linuxcnc status channel
try:
    Ls = linuxcnc.stat()
    print dir(Ls.poll())
except linuxcnc.error as detail:
    print("Error:", detail)
    sys.exit(1)

try:
    Lc = linuxcnc.command()
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
