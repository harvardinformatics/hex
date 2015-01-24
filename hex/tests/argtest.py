#!/usr/bin/env python

"""
Created on Oct 8, 2014
Copyright (c) 2014
Harvard FAS Research Computing
All rights reserved.

@author: Aaron Kitzmiller
"""
import sys
from argparse import ArgumentParser,RawDescriptionHelpFormatter

def main(): 
    parser = ArgumentParser(description="Argument type tester", \
        formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument("--boolean-option",help="Option that is either set or not.", action='store_true')
    parser.add_argument("--optional-option",help="Option with an optional argument.", nargs='?',const='x')
    parser.add_argument("--option",help="Option with an argument", nargs=1)
    parser.add_argument("--quoted-option",help="Option with an argument.  cmd pattern has single quotes", nargs=1)
    parser.add_argument("arg",help="Positional argument", nargs=1)
    
    # Process arguments
    args = parser.parse_args()
    if args.boolean_option:
        print "Boolean option set"
    if args.optional_option:
        if args.optional_option != 'x':
            print "Optional option value %s" % args.optional_option
        else:
            print "Optional option set"
    if args.optional_option != 'x':
        print "Optional option value %s" % args.optional_option
    if args.option:
        print "Option set to %s" % args.option[0]
    if args.quoted_option:
        print "Quoted option set to %s" % args.quoted_option[0]
    if args.arg:
        print "Arg set to %s" % args.arg[0]

if __name__ == "__main__":
    sys.exit(main())
    
 