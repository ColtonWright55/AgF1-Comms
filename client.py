import socket
import threading
import time
import re
from collections import deque
from utils import receive_data

HOST = '172.30.95.50'  # The server's hostname or IP address
PORT = 12345  # The port used by the server

def load_gcode_lines(filepath):
    commands = []
    with open(filepath, 'r') as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line:
                continue
            # Remove parenthetical comments anywhere in the line
            line = re.sub(r"\([^)]*\)", "", line).strip()
            if not line:
                continue
            # Skip lines containing percent program markers
            if '%' in line:
                continue
            commands.append(line)
    return commands


class MotionGate():
    def __init__(self):
        self.lock = threading.Lock()
        self.cur_command = None
        self.idle = True

    def on_status(self, data):
        try:
            cur_command = data.get('command')
        except Exception:
            pass
        self.is_idle()

    def is_idle(self):
        with self.lock:
            if self.cur_command != '': # If no command is running, ready to send a new one
                self.idle = True
            else:
                self.idle=False


def send_sequentially(sock, commands, gate):
    for cmd in commands:
        sock.sendall(cmd.encode('utf-8'))
        time.sleep(0.02)
        while not gate.is_idle():
            time.sleep(0.02)
        time.sleep(0.02)  # brief settle when done with gcode file


if __name__ == '__main__':
    gcode_path = 'gcode/3-4Bolt__25A'
    lines = load_gcode_lines(gcode_path)


    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print("Connected")

        gate = MotionGate()
        threading.Thread(target=receive_data, args=(s, gate.on_status), daemon=True).start()

        send_sequentially(s, lines, gate)

        print("All commands sent. Shutdown")