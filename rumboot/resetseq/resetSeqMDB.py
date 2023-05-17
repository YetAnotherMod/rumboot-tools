import os
import time
import usb.core
import pygpiotools
import usb.util
from parse import parse
from rumboot.resetseq.resetSeqBase import base
from serial import Serial

class mdb(base):
    name = "Malina Debug Bridge"
    swap   = False
    supported = ["POWER", "RESET", "HOST", "ELOCK"]

    def __init__(self, terminal, opts):
        port = os.path.realpath(terminal.ser._port)
        self.ctlport = opts["mdb_ctl_port"]
        if self.ctlport is None:
            id = parse("/dev/ttyACM{:d}", port)[0]
            id += 1
            self.ctlport = f"/dev/ttyACM{id}"
        self.serial = Serial(self.ctlport, 115200)        
        super().__init__(terminal, opts)
        self["ELOCK"] = 0
        self["HOST"] = 0

    def __setitem__(self, key, value):
        super().__setitem__(key, value)

        if "HOST" in self._states:
            self.serial.write(f"HOST {self._states['HOST']}\r\n".encode())

        if "ELOCK" in self._states:
            self.serial.write(f"ELOCK {self._states['ELOCK']}\r\n".encode())

        if "RESET" in self._states:
            self.serial.write(f"RESET {1 - self._states['RESET']}\r\n".encode())

    def get_options(self):
        return {
                "mdb-ctl-port" : {
                    "help" : "Malina Debug Bridge control port",
                    "default" : None,
                },
            }