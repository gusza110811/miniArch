import sys, threading
from collections import deque

class Rom:
    def __init__(self,data:bytearray):
        self.data = data
        self.datalen = len(data)
    
    def loadb(self, address:int) -> int:
        if address < self.datalen:
            return self.data[address]
        else:
            return 0

class Ram:
    def __init__(self):
        self.values = bytearray(0xFFFFF)

    def loadb(self, address:int) -> int:
        return self.values[address]

    def storeb(self, address:int, value:int):
        self.values[address] = value

class Memory:
    def __init__(self,rom:bytearray):
        self.ram = Ram()
        self.rom = Rom(rom)

        self.storeb = self.ram.storeb
    
    def loadb(self,address:int):
        if address >= 0xF0000:
            return self.rom.loadb(address-0xF0000)
        else:
            return self.ram.loadb(address)
    
    def shadow(self):
        self.loadb = self.ram.loadb

class Port:
    def __init__(self):pass
    def write(self):pass
    def read(self):pass

class uartDev:
    def __init__(self):
        self.inbuffer = deque()
        self.outbuffer = ''
        self.stdin = sys.stdin

        self.rx_ready = False
        self.tx_ready = True
    def inputThread(self):
        self.inbuffer.append(self.stdin.read(1))
        self.rx_ready = True
    
    def outputThread(self):
        if self.outbuffer:
            self.tx_ready = False
            print(self.outbuffer,end="",flush=True)
            self.outbuffer = ''
            self.tx_ready = True

class IO:
    # ~64k ports
    # 0x0300 - 0x030F : UART
    # 0x0310 - 0x031F : Timer
    def __init__(self):
        self.nextPort = 0x300
        self.ports:dict[int,Port] = {}
    
    def getPort(self):
        port = Port()
        self.ports[self.nextPort] = port
        self.nextPort += 1
        return port
