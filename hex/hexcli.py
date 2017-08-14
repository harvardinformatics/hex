#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
hex command line tool

Collects options and hands off to subcommands

@date      : 2017-06-20 13:19:21
@author    : Aaron Kitzmiller (aaron_kitzmiller@harvard.edu)
@version   : $Id$
@copyright : 2017 The Presidents and Fellows of Harvard College. All rights reserved.
@license   : GPLv2
"""
import os,sys,traceback
import logging
from argparse import ArgumentParser,RawDescriptionHelpFormatter
from hex import __version__ as version
from hex import UserException

SUBCOMMAND_MODULES = [
    ("exec","Execute a command directly, without argument processing","hexexec"),  # subcommand name, description, modulename
]

logger = logging.getLogger("hex")


def applyParameterDefToArgumentParser(parameterdef,parser):
    """
    Applies a parameterdef into an argparse parser
    """
    switches = parameterdef.pop("switches")
    if not isinstance(switches, list):
        switches = [switches]

    # Gotta take it off for add_argument
    # Positional arguments will not have a name
    name = None

    if "name" in parameterdef:
        name = parameterdef.pop("name")
        parameterdef["dest"] = name
    if "default" in parameterdef:
        parameterdef["help"] += "  [default: %s]" % parameterdef["default"]
    parser.add_argument(*switches,**parameterdef)

    # Gotta put it back on for later
    if name is not None:
        parameterdef["name"] = name


def initArgs():
    '''
    Setup arguments with parameterdef, check envs, parse commandline.
    Returns args as a dictionary
    '''

    # Parameter defs for the main command
    parameterdefs = [
        {
            'name'      : 'HEX_LOGLEVEL',
            'switches'  : ['--loglevel'],
            'required'  : False,
            'help'      : 'Log level (e.g. DEBUG, INFO)',
            'default'   : 'INFO',
        },
        {
            'name'      : 'RUNLOGGER',
            'switches'  : ['--runlogger'],
            'required'  : False,
            'help'      : 'Optional, logging in addition to default file logging (e.g. sql)'
        }
    ]

    # Check for environment variable values
    # Set to 'default' if they are found
    for parameterdef in parameterdefs:
        if os.environ.get(parameterdef['name'],None) is not None:
            parameterdef['default'] = os.environ.get(parameterdef['name'])

    # Setup argument parser
    description = """Harvard Executables"""

    parser = ArgumentParser(description=description,formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument('-V', '--version', action='version', version=version)

    # Use the parameterdefs for the ArgumentParser
    for parameterdef in parameterdefs:
        applyParameterDefToArgumentParser(parameterdef,parser)

    # Setup the subcommands and their parameters
    subparsers = parser.add_subparsers(help='hex subcommands',dest='SUBCOMMAND')
    for subcommand,description,modulestr in SUBCOMMAND_MODULES:
        modulename = 'hex.subcommand.%s' % modulestr
        module = __import__(modulename,globals(),locals(),['getParameterDefs'])
        parameterdefs = module.getParameterDefs()
        parsernew = subparsers.add_parser(subcommand, description=description)
        for parameterdef in parameterdefs:
            applyParameterDefToArgumentParser(parameterdef,parsernew)

    # Convert the args object into a dictionary
    args = parser.parse_args()
    argdict = {}
    for attr in dir(args):
        if not attr.startswith('__') and not callable(getattr(args,attr)):
            argdict[attr] = getattr(args,attr)
    return argdict


def main():
    """
    Main function.
    """
    try:
        argdict = initArgs()

        # Set loglevel
        try:
            loglevel = int(logging.getLevelName(argdict['HEX_LOGLEVEL']))
        except ValueError as e:
            raise UserException('--loglevel / HEX_LOGLEVEL value %s is not recognized.' % argdict['HEX_LOGLEVEL'])
        logger.setLevel(loglevel)

        # Run the subcommand
        for subcommandstr,description,modulestr in SUBCOMMAND_MODULES:
            if argdict["SUBCOMMAND"] == subcommandstr:
                modulename = 'hex.subcommand.%s' % modulestr
                func = getattr(__import__(modulename,globals(),locals(),[modulestr]),modulestr)
                return func(argdict)

    except Exception as e:
        if isinstance(e,UserException):
            sys.stderr.write('\n%s\n\n' % e.user_msg)
            return 1
        else:
            sys.stderr.write('\n%s\n%s\n\n' % (str(e),traceback.format_exc()))
            return 1


if __name__ == "__main__":
    sys.exit(main())
