import sys
import time
import datetime
import numpy as np
import socket
import linuxcnc


# host can be a hostname, IP address or empty string
# IP address usually needs to be IPv4 formatted address string, for ex. 127.0.0.1
# empty string - server will accept connection from all available IPv interfaces
HOST = '127.0.0.1' # Standard loopback interface address (localhost)
# port should an integer between 1-65535 (0 is reserved)
PORT = 65432 # Port to listen on (non-privileged ports are > 1023)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # the value that this passed to bind() depends on the address family of the socket
    # for AF_INET(IPv4), bind() expects a tuple (host, port)
    s.bind((HOST, PORT))
    s.listen()

    # When a client connects, it returns
    # conn - a new socket object representing the connection
    # addr - a tuple holding the address of the client (host, port) for IPv4 or (host, port, flowinfo, scopeid) for IPv6
    conn, addr = s.accept()

    # conn is a different socket from 's' which was the original socket used to listen to and accept new connections
    with conn:
        print("Connected by", addr)

        # an infinite while loop is used to loop over blocking calls to conn.recv().
        # here it will read whatever data the client send and echoes it back using conn.sendall()
        while True:
            data = conn.recv(1024)
            
            # if conn.recv() returns an empty bytes object, b'', then the loop is terminated
            if not data:
                break
            conn.sendall(data)