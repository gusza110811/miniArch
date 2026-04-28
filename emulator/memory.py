import os
import sys, threading
import waiting
from collections import deque
from enum import Enum
from io import BufferedRandom

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
    def read(self) -> int:return 0

class Register(Port):
    def __init__(self,readonly):
        self.value = 0
        if readonly:
            self.write = lambda x: x
    def write(self, value):
        self.value = value
    def read(self):
        return self.value

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

class lbaDisk:
    class Command(Enum):
        read = 1
        write = 2
        queryDevice = 3
        querySize = 4
        clearBuffer = 5
    
    class Status(Enum):
        success = 0x00
        busy = 0x01
        invalidsector = 0x10
        invaliddevice = 0x11

    def __init__(self, getport):
        self.commandPort:Port = getport()
        self.commandPort.write = self.comW
        self.status:Register = getport(True,True)

        self.sector0:Register = getport(True)
        self.sector1:Register = getport(True)
        self.sector2:Register = getport(True)
        self.sector3:Register = getport(True)

        self.device:Register = getport(True)
        self.data:Port = getport()
        self.data.read = self.bufR
        self.data.write = self.bufW

        self.buffer = deque()

        self.disks:dict[int,BufferedRandom] = {}
    
    def get_size(self,file_object):
        original_position = file_object.tell()
        file_object.seek(0, os.SEEK_END)
        size = file_object.tell()
        file_object.seek(original_position)
        return size
    
    def comW(self, value):
        disk = self.disks.get(self.device.value)
        if not disk:
            self.status.value = self.Status.invaliddevice.value
            return
        sector = self.sector0.value + (self.sector1.value << 8) + (self.sector2.value << 16) + (self.sector3.value << 24)

        if sector*512 >= self.get_size(disk):
            self.status.value = self.Status.invalidsector.value
            return

        if value == self.Command.read.value:
            self.status.value = self.Status.busy.value
            threading.Thread(target=lambda: self.read(disk,sector)).start()
        elif value == self.Command.write.value:
            self.status.value = self.Status.busy.value
            threading.Thread(target=lambda: self.write(disk,sector)).start()
        elif value == self.Command.queryDevice.value:
            for i in range(256):
                if i in self.disks:
                    self.buffer.append(1)
                else:
                    self.buffer.append(0)
            self.status.value = self.Status.success.value
        elif value == self.Command.querySize.value:
            size = self.get_size(disk) >> 9
            self.buffer.append(size & 0xFF)
            self.buffer.append((size >> 8) & 0xFF)
            self.buffer.append((size >> 16) & 0xFF)
            self.buffer.append((size >> 24) & 0xFF)
            self.status.value = self.Status.success.value
        elif value == self.Command.clearBuffer.value:
            self.buffer.clear()
            self.status.value = self.Status.success.value
    
    def bufR(self):
        if self.buffer:
            return self.buffer.popleft()
        else:
            return 0
    
    def bufW(self, value):
        self.buffer.append(value)

    def write(self,disk,sector):
        disk.seek(sector*512)
        data = [self.buffer.popleft() if self.buffer else 0 for _ in range(512)]
        disk.write(bytes(data))
        self.status.value = self.Status.success.value
    
    def read(self,disk,sector):
        disk.seek(sector*512)
        self.buffer.extend(disk.read(512))
        self.status.value = self.Status.success.value

class IO:
    # 64ki ports
    # 0x0300 - 0x030F : UART
    # 0x0310 - 0x031F : Timer
    # 0x0320 - 0x0327 : Disk
    # 0xFFFF          : Debug Console
    def __init__(self):
        self.ports:dict[int,Port] = {}

        self.nextPort = 0xffff
        self.dbg = dbgComDev(self.getPort)

        self.nextPort = 0x0320
        self.disk = lbaDisk(self.getPort)
    
    def getPort(self, register=False, readonly=False):
        if register:
            port = Register(readonly)
        else:
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
