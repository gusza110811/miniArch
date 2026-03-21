import sys, threading
import waiting
from collections import deque

class Rom:
    def __init__(self,data:bytearray):
        self.data = data
        self.values = self.data
        self.datalen = len(data)
    
    def loadb(self, segment:int, address:int) -> int:
        addr = ((segment << 4) & 0xFFFF0) + (address&0xFFFF)
        if addr < self.datalen:
            return self.data[addr]
        else:
            return 0
    
    def loadw(self, segment:int, address:int) -> int:
        return self.loadb(segment,address) + (self.loadb(segment,address+1) << 8)

class Ram:
    def __init__(self):
        self.values = bytearray(0x100000)

    def loadb(self, segment:int, address:int) -> int:
        val = self.values[((segment << 4) + (address&0xFFFF)) & 0xFFFFF]
        self.lastAddr, self.lastValue = address, val
        #print(f"{segment:4X}:{address:4X}  {val:2X}\r")
        return val

    def storeb(self, segment:int, address:int, value:int):
        self.values[(((segment << 4) & 0xFFFF0) + (address&0xFFFF)) & 0xFFFFF] = value&0xff
        self.lastAddr, self.lastValue = address, value
    
    def loadw(self, segment:int, address:int) -> int:
        val = self.loadb(segment,address) | (self.loadb(segment,address+1) << 8)
        self.lastAddr, self.lastValue = address, val
        return val

    def storew(self, segment:int, address:int, value:int):
        self.storeb(segment,address,value)
        self.storeb(segment,address+1,value>>8)

class Memory:
    def __init__(self,rom:bytearray):
        self.ram = Ram()
        self.rom = Rom(rom)
        self.lastAddr = 0
        self.lastValue = 0
    
    def loadb(self,segment:int,address:int):
        if segment >= 0xF000:
            val = self.rom.loadb(segment-0xF000,address)
        else:
            val = self.ram.loadb(segment,address)
        self.lastAddr, self.lastValue = address, val
        return val

    def loadw(self, segment:int, address:int):
        if segment >= 0xF000:
            val = self.rom.loadw(segment-0xF000,address)
        else:
            val = self.ram.loadw(segment,address)
        self.lastAddr, self.lastValue = address, val
        return val

    def loadbs(self,segment:int,address:int):
        val = self.ram.loadb(segment,address)
        self.lastAddr, self.lastValue = address, val
        return val
    def loadws(self,segment:int,address:int):
        val = self.ram.loadw(segment,address)
        self.lastAddr, self.lastValue = address, val
        return val

    def storeb(self,segment:int,address:int,value:int):
        self.ram.storeb(segment,address,value)
        self.lastAddr, self.lastValue = address, value

    def storew(self,segment:int,address:int,value:int):
        self.ram.storew(segment,address,value)
        self.lastAddr, self.lastValue = address, value
    
    def lastAccess(self):
        return (self.lastAddr, self.lastValue)
    
    def shadow(self):
        self.loadb = self.loadbs
        self.loadw = self.loadws

class Port:
    def __init__(self):pass
    def write(self, value:int):pass
    def read(self) -> int:pass

class dbgComDev:
    def __init__(self, getPort):
        self.inbuffer = deque()
        self.outbuffer = deque()
        self.stdin = sys.stdin

        port:Port = getPort()
        port.read = self.read
        port.write = self.write

        self.inputThread = threading.Thread(target=self.input,daemon=True)
        self.outputThread = threading.Thread(target=self.output,daemon=True)

        self.inputThread.start()
        self.outputThread.start()

    def input(self):
        while 1:
            char = self.stdin.read(1)
            if char == "\x7F":
                self.inbuffer.append("\b")
            else:
                self.inbuffer.append(char)
    
    def output(self):
        while 1:
            if self.outbuffer:
                print(chr(self.outbuffer.popleft()),end="",flush=True)

    def read(self):
        if self.inbuffer:
            return ord(self.inbuffer.popleft())
        else:
            return 0
    
    def write(self, value:int):
        self.outbuffer.append(value)

class IO:
    # ~64k ports
    # 0x0300 - 0x030F : UART
    # 0x0310 - 0x031F : Timer
    # 0xFFFF          : Debug Console
    def __init__(self):
        self.nextPort = 0xffff
        self.ports:dict[int,Port] = {}

        self.dbg = dbgComDev(self.getPort)
    
    def getPort(self):
        port = Port()
        self.ports[self.nextPort] = port
        self.nextPort += 1
        return port
    
    def write(self, portid:int, value:int):
        port = self.ports.get(portid)
        if port:
            port.write(value&0xFF)
    
    def read(self, portid:int) -> int:
        port = self.ports.get(portid)
        if port:
            val = port.read()
            return val
        else:
            return 0
