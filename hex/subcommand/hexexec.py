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
from hex.system import getSystem


def getParameterDefs():

    parameterdefs = [
        {
            'name'      : 'CMD_SPEC',
            'help'      : 'Command specification',
        },
    ]
    return parameterdefs


def hexexec(args):
    """
    Direct execution of the command with no argument processing
    """
    system  = getSystem(args)
    cmd     = ' '.join(args['CMD_SPEC'],args['CMD_ARGS'])
    system.execute(cmd)
