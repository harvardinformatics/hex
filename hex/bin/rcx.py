#!/usr/bin/env python
"""
Created on Sep 25, 2014
Copyright (c) 2014
Harvard FAS Research Computing
All rights reserved.

@author: Aaron Kitzmiller

Runs a command and logs details of execution.

By default the logger is a FileWriter that writes to a small name: value file
in the project directory.  Other loggers can be used that write to sqllite or mysql
databases.

For the process, the following values are logged:
    jobid  - job id for submitted jobs, process id for run jobs
    cmdstring - command string
    starttime  - datetime the job was started
    endtime    - datetime the job ended
    env    - the environment variables ?!? 
    
"""

import sys, os
from command import Command,getClassFromName

from argparse import ArgumentParser, RawDescriptionHelpFormatter, REMAINDER

def main(): 
    '''Command line options.'''
#     try:
    # Setup argument parser
    parser = ArgumentParser(description="Run commands and log process details", \
        formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument("--rcx-runsetname",help="Run set name.  Used as a file name for the process log.", nargs="?")
    parser.add_argument("--rcx-jobtype",help="Is this a 'submit' or 'run' job?  \
        Jobs that are 'submitted' will be launched and detached.  A subsequent process \
        will need to be run to get end time, exit code, etc.  If the job type is 'run', \
        rcx.py will wait until its finished.", nargs="?", default="run")
    parser.add_argument("--rcx-runsetpath",help="Path for storing the runset.", nargs="?")
    parser.add_argument("--rcx-logger",help="Logger class",default="cmd.DefaultFileLogger", nargs="?")
    parser.add_argument("--rcx-runner",help="Runner class",default="cmd.ShellRunner", nargs="?")
    parser.add_argument("--rcx-stdoutfile",help="File name for piping stdout", nargs="?")
    parser.add_argument("--rcx-stderrfile",help="File name for piping stderr", nargs="?")
    parser.add_argument("cmd",nargs=REMAINDER,help="Command line to be run")
    
    # Process arguments
    args = parser.parse_args()
    
    # Fail if there is no cmd
    if not args.cmd:
        print "No command was given to run"
        parser.print_help()
        exit(1)
        
    
    # Setup the logger
    logger = None
    cls = getClassFromName(args.rcx_logger)
    if (args.rcx_runsetpath):
        logger = cls(pathname=args.rcx_runsetpath)
    else:
        logger = cls()
    
    # Setup the runner
    cls = getClassFromName(args.rcx_runner)
    runner = cls(logger=logger)
    
    runargs = {}
    if args.rcx_stdoutfile:
        runargs['stdoutfile'] = os.path.abspath(args.rcx_stdoutfile)
    if args.rcx_stderrfile:
        runargs['stderrfile'] = os.path.abspath(args.rcx_stderrfile)
    if args.rcx_runsetname:
        runargs['runsetname'] = args.rcx_runsetname
    
    h = runner.run(' '.join(args.cmd),**runargs)
    if args.rcx_jobtype == 'run':
        h.wait()
        print h.stdoutstr
    else:
        print h.jobid
    
        

if __name__ == "__main__":
    sys.exit(main())
