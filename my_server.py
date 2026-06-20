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
PORT = 1234



print "Testing LinuxCNC"
while True:
    try:
        s = linuxcnc.stat()
        if s.poll():
            break
    except Exception, e:
        print "LinuxCNC not ready yet (%s), retrying..." % e
        time.sleep(1)

print "LinuxCNC ready"

print "Testing network"
while True:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1.0)
    try:
        s.bind((HOST,PORT))
        s.close()
        break
    except socket.error:
        print "Socket not available, retrying..."
        time.sleep(1)

print "Network ready"

# Loop until exactly n bytes received — TCP can split a single message across multiple recv() calls
def recvall(conn, n):
    buf = b''
    while len(buf) < n:
        chunk = conn.recv(n - len(buf))
        if not chunk:
            return None
        buf += chunk
    return buf

def handle_client(conn):
    conn.settimeout(5.0)
    stop = threading.Event()

    def send_data():
        while not stop.is_set():
            Ls.poll()
            data = {field: getattr(Ls, field) for field in fields}
            data['timestamp'] = datetime.datetime.now().isoformat()

            message = json.dumps(data)
            message_bytes = message.encode('utf-8')
            try:
                conn.sendall(struct.pack('!I', len(message_bytes)))
                conn.sendall(message_bytes)
            except socket.error:
                stop.set()
                break

            time.sleep(sample_interval)

    def receive_commands():
        while not stop.is_set():
            try:
                raw_len = recvall(conn, 4)
                if raw_len is None:
                    print "Client Disconnected"
                    break
                msg_len = struct.unpack('!I', raw_len)[0]
                raw_cmd = recvall(conn, msg_len)
                if raw_cmd is None:
                    print "Client Disconnected"
                    break
                cmd = raw_cmd.decode('utf-8').strip('\023')
                if not cmd:
                    continue
                print "received command: ", cmd

                if ok_for_mdi():
                    try:
                        Lc.mode(linuxcnc.MODE_MDI)
                        Lc.wait_complete(2.0)
                        Lc.mdi(cmd)
                    except Exception as e:
                        print "MDI error: ", e
                else:
                    print "Not ready for MDI, dropping command: ", cmd
            except socket.timeout:
                continue
            except socket.error as e:
                print "Client Disconnected: ", e
                break
        stop.set()

    t = threading.Thread(target=send_data)
    t.daemon = True
    t.start()
    receive_commands()
    stop.set()

def ok_for_mdi():
    Ls.poll()
    return not Ls.estop and Ls.enabled and (Ls.interp_state == linuxcnc.INTERP_IDLE)






# Connect to linuxcnc status channel
try:
    Ls = linuxcnc.stat()
    # print dir(Ls.poll())
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

sample_rate = 20
sample_interval = 1.0 / sample_rate





s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
    s.bind((HOST, PORT))
    s.listen(5)
    while True:
        conn, addr = s.accept()
        print "Connected by", addr

        handle_client(conn)
        conn.close()
finally:
    s.close()