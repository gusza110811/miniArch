import sys
from collections import deque

class Ram:
    def __init__(self):
        self.values:dict[int,int] = {}

    def load(self, address:int) -> int:
        return self.values.get(address,0)

    def store(self, address:int, value:int):
        self.values[address] = value

class IO:
    # ~64k ports
    # 0x0300 - 0x030F : Serial Ports
    # 0x0310 - 0x031F : Timers
    def __init__(self):
        pass
    
    def write(self, address:int, value:int):
        pass

class SerialPorts:
    def __init__(self):
        self.buffer = deque()
        self.stdin = sys.stdin
    def bufferThread(self):
        self.buffer.append(self.stdin.read(1))
