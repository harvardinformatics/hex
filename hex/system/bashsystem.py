#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Manages the interactions with a bash-based system, including the construction and
running of scripts 

@date      : 2017-06-20 13:29:55
@author    : Aaron Kitzmiller (aaron_kitzmiller@harvard.edu)
@copyright : 2017 The Presidents and Fellows of Harvard College. All rights reserved.
@license   : GPLv2
"""

import os, socket, sys, logging
import time
from subprocess import Popen,PIPE
import tempfile
from textwrap import TextWrapper
from hex import __version__,UserException
from hex.runlog import RunLog, DefaultRunLogger
from datetime import datetime

# If a custom bash script template is needed, specify the path to it with the BASH_SYSTEM_TEMPLATE env var
BASH_SYSTEM_TEMPLATE_PATH = os.environ.get('BASH_SYSTEM_TEMPLATE')

# The default bash script dir is ~/.hex/bashscripts
DEFAULT_BASH_SCRIPTDIR = os.path.expanduser("~/.hex/bashscripts")

logger = logging.getLogger("hex")


class BashSystem(object):
    """
    Basic bash interpreter system. 

    If no runlogger is specified the DefaultRunLogger is used.

    If interpreter is specified, it should be the full path.
    """
    def __init__(self,interpreter="/bin/bash",scriptsuffix=".sh",runlogger=None,**kwargs):
        self.interpreter = interpreter
        self.scriptsuffix = scriptsuffix

        if runlogger is None:
            runlogger = DefaultRunLogger()

        self.runlogger = runlogger

        self.default_template = """{comment}

{content}
"""
        if BASH_SYSTEM_TEMPLATE_PATH is not None:
            try:
                templatestr = ""
                with open(BASH_SYSTEM_TEMPLATE_PATH,"r") as f:
                    templatestr = f.read()
                self.default_template = templatestr
            except Exception as e:
                raise UserException("Unable to read bash template %s: %s" % (BASH_SYSTEM_TEMPLATE_PATH,str(e)))

    def getTemplate(self):
        return self.default_template

    def formatComment(self,comment):
        """
        Formats a string as a bash comment
        """
        # Replace newlines with a \n#
        comment = comment.replace("\n","\n# ")
        textwidth = 60  # 60 char comments
        wrapper = TextWrapper(replace_whitespace=False,width=textwidth,initial_indent="# ",subsequent_indent="# ")
        if comment is None or comment.strip() == "":
            return ""
        return wrapper.fill(comment)

    def defaultComment(self):
        """
        Default comment string placed at the top of each script
        """
        return "bash script composed by hex version %s on %s" % (__version__,str(datetime.now()))

    def compose(self,**kwargs):
        """
        Composes a bash script string using the kwargs

        Base system uses only a 'content' kwarg.  
        A 'comment' kwarg is strongly recommended.

        Subclasses should call this after composing a 'content' string
        """
        if "content" not in kwargs:
            raise UserException("BashSystem compose requires a content keyword argument.")
        comment = self.defaultComment()
        if "comment" in kwargs:
            comment = kwargs["comment"]
        comment = self.formatComment(comment)
        templatestr = self.getTemplate()
        return templatestr.format(comment=comment,content=kwargs["content"])

    def makeScriptFile(self,scriptcontents,runid=None,scriptpath=None):
        """
        Write a script file using scriptcontents and return the file path.

        If scriptpath is specified, it will be used.
        If runid is specified, the runlogger will be used to create a scriptpath
        If scriptpath is not specified, and runid is not specified, an os tempfile will be created.
        Tempfiles that are created are not removed.
        """

        if scriptpath is None:
            if runid is not None and runid.strip() != "":
                scriptpath = self.runlogger.getScriptPath(runid,self.scriptsuffix)

                # Create the directory if necessary
                scriptdir = os.path.dirname(scriptpath)
                if not os.path.exists(scriptdir):
                    os.makedirs(scriptdir)

                scripth = open(scriptpath,'w')
            else:
                scripth = tempfile.NamedTemporaryFile(suffix=self.scriptsuffix,delete=False)
                scriptpath = scripth.name

        # Write contents and return path
        scripth.write(scriptcontents + "\n")
        return scriptpath

    def executeScript(self,scriptfilepath,runid=None,stdoutfile=None,stderrfile=None,cmd=None,monitor=True):
        """
        Launches the script file, waits for it to complete,  
        and logs it with the run logger.  Returns the runid assigned by the RunLogger.

        If runid is not set, the RunLogger will generate a new one.

        If stdoutfile or stderrfile are not set, the stdout / stderr lines are printed

        cmd is the command being run and is only for annotation purposes
        """
        hostname = socket.gethostname().split('.',1)[0]
        args = [self.interpreter,scriptfilepath]

        # Setup stdout
        if stdoutfile is None and runid is not None:
            stdoutfile = self.runlogger.getStdOutPath(runid)
        if stdoutfile is None:
            stdout = PIPE
        else:
            stdout = open(stdoutfile,'w')

        # Setup stderr
        if stderrfile is None and runid is not None:
            stderrfile = self.runlogger.getStdErrPath(runid)

        if stderrfile is None:
            stderr = PIPE
        else:
            stderr = open(stderrfile,'w')

        proc = Popen(args,stdout=stdout,stderr=stderr)

        # Save the run log
        runlog = RunLog(
            runid=runid,
            interpreter=self.interpreter,
            scriptfilepath=scriptfilepath,
            jobid=proc.pid,
            starttime=datetime.now(),
            system="%s.%s" % (self.__module__, self.__class__.__name__),
            hostname=hostname,
            status="RUNNING",
            cmd=cmd,
        )
        if stdoutfile is not None:
            runlog["stdoutfile"] = stdoutfile
        if stderrfile is not None:
            runlog["stderrfile"] = stderrfile
        runid = self.runlogger.save(runlog)

        # Execute and wait
        if monitor:
            if stdoutfile is None:
                stdouth = proc.stdout
            else:
                stdouth = runlog.getStdOutHandle()
            if stderrfile is None:
                stderrh = proc.stderr
            else:
                stderrh = runlog.getStdErrHandle()

            while proc.poll() is None:
                sys.stdout.write(stdouth.readline())
                sys.stderr.write(stderrh.readline())
            sys.stdout.flush()
            sys.stderr.flush()
        else:
            proc.wait()

        # Update the run log with the result
        runlog = self.runlogger.get(runid)
        runlog["endtime"] = datetime.now()
        runlog["status"] = "COMPLETED"
        if proc.returncode == 0:
            runlog["result"] = "SUCCESS"
        else:
            runlog["result"] = "FAIL"

        return self.runlogger.save(runlog)

    def execute(self,cmds,stdoutfile=None,stderrfile=None,runid=None,monitor=True):
        """
        Execute a command synchronously.

        cmd may be either a string or a list.  A list is 
        treated as several commands.

        Creates the script file from the command(s), runs the command, 
        and logs it.

        If monitor is True, then stdout and stderr will be printed to the console.
        """
        # Setup command string
        if isinstance(cmds,basestring):
            cmds = [cmds]
        cmdstr = "\n".join(cmds)

        # If runid is none, we need to get one so that the runlogger can keep everything together
        if runid is None:
            runid = self.runlogger.newRunId(cmd=cmdstr)

        return self.executeScript(
            self.makeScriptFile(
                self.compose(content=cmdstr),
                runid=runid,
            ),
            runid=runid,
            stdoutfile=stdoutfile,
            stderrfile=stderrfile,
            cmd=cmdstr,
            monitor=monitor,
        )

    def launch(self,cmds,stdoutfile=None,stderrfile=None,runid=None,monitor=False):
        """
        Executes a command asynchronously by forking a call to the execute() method.  
        Waits until runlog has been initiated before it returns.
        If after 10 attempts, the runlog is still not created an exception is thrown.
        """

        # Make sure we can return the runid 
        if isinstance(cmds,basestring):
            cmds = [cmds]
        cmdstr = "\n".join(cmds)
        if runid is None:
            runid = self.runlogger.newRunId(cmd=cmdstr)

        pid = os.fork()
        if pid == 0:
            self.execute(cmds,stdoutfile,stderrfile,runid,monitor)
            os._exit(0)
        else:
            max_attempts = 10
            attempts = 0
            sleepytime = 5
            error = ""
            while attempts <= max_attempts:
                try:
                    self.runlogger.get(runid)
                    return runid
                except Exception as e:
                    error = str(e)
                    time.sleep(sleepytime)
                    attempts += 1
            raise Exception("Launch of command(s) %s has not created a valid runlog: %s" % (str(cmds),error))
