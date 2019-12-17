from classes.chipDb import ChipDb
from classes.ImageFormatDb import ImageFormatDb
from classes.resetSeq import ResetSeqFactory
from classes.cmdline import arghelper
from classes.terminal import terminal

import argparse
import rumboot_xrun
from parse import *

def cli():
    resets  = ResetSeqFactory("classes.resetseq")
    formats = ImageFormatDb("classes.images")
    chips   = ChipDb("classes.chips")

    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description="rumboot-xrun {} - RumBoot X-Modem execution tool\n".format(rumboot_xrun.__version__) +
                                    "(C) 2018 Andrew Andrianov, RC Module\nhttps://github.com/RC-MODULE")
    arghelper.add_file_handling_opts(parser)
    arghelper.add_terminal_opts(parser)
    arghelper.add_resetseq_options(parser, resets)
    plus = parser.add_argument_group("Plusargs parser options", 
        """
        rumboot-xrun can parse plusargs (similar to verilog simulator) 
        and use them for runtime file uploads. This option is intended 
        to be used for 
        """)
    plus.add_argument('-A', '--plusargs', nargs='*')

    opts = parser.parse_args()

    plusargs = {}
    if opts.plusargs:
        for a in opts.plusargs:
            ret = parse("+{}={}", a)
            if ret:
                plusargs[ret[0]] = ret[1]
                continue
            ret = parse("+{}", a)
            if ret: 
                plusargs[ret[0]] = True                

    c = arghelper.detect_chip_type(opts, chips, formats)
    if c == None:
        return 1
        
    print("Detected chip:    %s (%s)" % (c.name, c.part))
    if c == None:
        print("ERROR: Failed to auto-detect chip type")
        return 1
    if opts.baud == None:
        opts.baud = [ c.baudrate ]

    reset = resets[opts.reset[0]]()
    term = terminal(opts.port[0], opts.baud[0])
    term.plusargs = plusargs

    if opts.log:
        term.logstream = opts.log

    print("Reset method:     %s" % (reset.name))
    print("Baudrate:         %d bps" % int(opts.baud[0]))
    print("Port:             %s" % opts.port[0])
    reset.resetToHost()
    term.xmodem_send_stream(opts.file, desc="Uploading image")
    return term.loop()
    
