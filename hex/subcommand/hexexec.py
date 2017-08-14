# -*- coding: utf-8 -*-

"""
exec subcommand

Directly runs a command line string without embellishment.

@date      : 2017-06-20 13:22:27
@author    : Aaron Kitzmiller (aaron_kitzmiller@harvard.edu)
@version   : $Id$
@copyright : 2017 The Presidents and Fellows of Harvard College. All rights reserved.
@license   : GPLv2
"""
import argparse
import logging
from hex.system import getAvailableSystems,getSystem
from hex.runlog import getRunLogger

logger = logging.getLogger("hex")
AVAILABLE_SYSTEMS = getAvailableSystems()


def getParameterDefs():

    parameterdefs = [
        {
            "switches"  : "--system",
            "help"      : "Script building and execution system.  Available systems: %s" % ", ".join(AVAILABLE_SYSTEMS.keys()),
            "name"      : "SYSTEM",
            "default"   : "bash",
        },
        {
            "switches"  : "CMD_SPEC",
            "help"      : "Command specification",
        },
        {
            "switches"  : "CMD_ARGS",
            "help"      : "Command arguments",
            "nargs"     : argparse.REMAINDER,
        }
    ]
    return parameterdefs


def hexexec(args):
    """
    Direct execution of the command with no argument processing
    """

    # Create the system
    systemkey = args["SYSTEM"]
    runlogger = getRunLogger(runlogger = args["RUNLOGGER"])
    system = getSystem(systemkey, runlogger = runlogger)
    cmd     = " ".join([args["CMD_SPEC"]] + args["CMD_ARGS"])
    system.execute(cmd)
