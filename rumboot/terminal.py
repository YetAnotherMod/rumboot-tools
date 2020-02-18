import serial
import sys
from xmodem import XMODEM
import os
from parse import parse
import time
import io
from tqdm import tqdm
from rumboot.OpFactory import OpFactory
from rumboot.chips.base import chipBase
import socket

class terminal:
        verbose=True
        logstream=None
        plusargs={}
        runlist = []
        chip = chipBase()
        dumps = {}
        curbin = "bootrom"

        def __init__(self, port, speed):
            self.port = port
            if self.port.find("://") < 0:
                self.ser = serial.Serial(port, speed, timeout=5)
            else:
                self.ser = serial.serial_for_url(port, timeout=5)

            def getc(size, timeout=10):
                ret = self.ser.read(size)
                return ret or None
            def putc(data, timeout=10):
                return self.ser.write(data)  # note that this ignores the timeout
            self.modem = XMODEM(getc, putc)
            self.opf = OpFactory("rumboot.ops", self) 
        
        def set_chip(self, chip):
            self.chip = chip

        def add_binaries(self, path):
            if type(path) is list:
                for p in path:
                    self.runlist.append(p[0])
            else:
                self.runlist.append(path)

        def add_dumps(self, dumps):
            self.dumps.update(dumps)

        def next_binary(self):
            if len(self.runlist) > 0:
                ret = self.runlist.pop(0)                
                self.curbin = ret
                return ret
            return None

        def current_binary(self):
            return self.curbin

        def current_dump(self):
            if self.curbin.name in self.dumps:
                return self.dumps[self.curbin.name]

        def log(self, *args, **kwargs):
            # Sometimes we get a weird exception on certain windows systems/setups
            # Try to catch any exceptions and dispose of them here
            try:
                if self.verbose:
                    tqdm.write(*args, **kwargs)
                    sys.stdout.flush()
                if not self.logstream == None:
                    self.logstream.write(*args)
                    self.logstream.write("\n")
            except:
                pass


        def sync(self):
            self.ser.reset_input_buffer()
            c1 = b'a'
            c2 = b'd'
            while True:
                c2 = self.ser.read(1)
                if c1 == b'U' and c2 == b'\r':
                    break
                if c1 == b'U' and c2 == b'\n':
                    break
                c1 = c2


        def loop(self, break_after_uploads=False):
            if not self.chip.skipsync:
                self.sync()
            while True:
                ret = None
                line = self.ser.readline()
                if line == b'':
                    continue
                try: 
                    line = line.decode().rstrip()
                except:
                    continue

                ret = self.opf.handle_line(line)
                if type(ret) is int:
                    return ret
                
                if break_after_uploads and len(self.runlist) == 0:
                    break
 
        def xmodem_send(self, fl, chunksize=0, desc="Uploading file", welcome=b"boot: host: Hit 'X' for xmodem upload\n"):
            stream = open(fl, 'rb')
            ret = self.xmodem_send_stream(stream, chunksize, welcome, desc)
            stream.close()
