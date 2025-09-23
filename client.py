import socket
import threading
import time
import re
from collections import deque
from utils import rcv_data, rcv_cmd

FORGE_HOST = '172.30.95.50'  # The server's hostname or IP address
FORGE_PORT = 1234  # The port used by the server

TPGEN_HOST = '' # For rcv commands from ToolpathGen
TPGEN_PORT = 123


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
        self.cmd_deque = deque()
        self.idle = True
        self.last_time = time.time()

    def on_status(self, data):
        try:
            cur_command = data.get('command')
        except Exception:
            pass
        print(data)
        print(f"Hz: {1/(time.time()-self.last_time)}")
        self.last_time = time.time()
        self.is_idle()

    def is_idle(self):
        with self.lock:
            if self.cur_command != '': # If no command is running, ready to send a new one
                self.idle = True
            else:
                self.idle=False

    def on_cmd(self):
        pass
        


    def send_sequentially(self, sock, commands, gate):
        for cmd in commands:
            print(f"Sending command: {cmd}")
            sock.sendall(cmd.encode('utf-8'))
            time.sleep(0.02)
            while not gate.idle:
                time.sleep(0.02)
            time.sleep(0.02)  # brief settle when done with gcode file


if __name__ == '__main__':
    gate = MotionGate()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tpg_s:
        
            # tpg_s.bind((TPGEN_HOST, TPGEN_PORT))
            # tpg_s.listen()
            # conn, addr = tpg_s.accept()
            # with conn:


                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as f_s:
                    f_s.connect((FORGE_HOST, FORGE_PORT))
                    print("Connected")

                    threading.Thread(target=rcv_data, args=(f_s, gate.on_status), daemon=True).start()
                    # threading.Thread(target=rcv_cmd, args=(conn, gate.on_cmd), daemon=True).start()
                    while True:
                        time.sleep(0.01)


