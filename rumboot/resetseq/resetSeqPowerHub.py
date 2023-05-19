import os
import time
import usb.core
import pygpiotools
import usb.util
from parse import parse
from rumboot.resetseq.resetSeqBase import base
import usb.core
import usb.util

# find our device


class powerhub(base):
    name = "PowerHub"
    swap   = False
    supported = ["POWER", "RESET"]
    mapping = {
        "POWER" : 0,
        "RESET" : 1
    }

    def __init__(self, terminal, opts):
        super().__init__(terminal, opts)
        self.dev = usb.core.find(idVendor=0x1d50, idProduct=0x6032) #ToDo: Serial
        self.port_id = int(opts["powerhub_usb_port"])

    def __setitem__(self, key, value):
        super().__setitem__(key, value)

        if key != "POWER":
            return 

        reqType = usb.util.CTRL_TYPE_VENDOR | usb.util.CTRL_RECIPIENT_OTHER | usb.util.ENDPOINT_OUT
        bReq = 3 #MethodCall
        wVal = 0
        wIndex = 10 #methodId

        data = bytes([self.port_id, value])
        ret = self.dev.ctrl_transfer(reqType, bReq, wVal, wIndex, data)



    def get_options(self):
        return {
#                "powerhub-use-outlet" : {
#                    "help" : "Use powerhub HV outlet",
#                    "default" : False,
#                    "action"  : 'store_true'
#                },
                "powerhub-usb-port" : {
                    "help" : "powerhub port number",
                    "default" : 1,
                }
            }