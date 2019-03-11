# -*- coding: utf-8 -*-

"""
BashSystem tests

@date      : 2017-07-18 13:03:33
@author    : Aaron Kitzmiller (aaron_kitzmiller@harvard.edu)
@version   : $Id$
@copyright : 2017 The Presidents and Fellows of Harvard College. All rights reserved.
@license   : GPLv2

"""
import unittest, os
import time
from hex.system import BashSystem
from hex.runlog import DefaultRunLogger

NON_DEFAULT_RUNLOG_PATH = "/tmp/runlogsfortesting"
ALTERNATE_RUNLOG_PATH = "/tmp/altrunlog"


class TestBashSystem(unittest.TestCase):

    def setUp(self):
        for d in [NON_DEFAULT_RUNLOG_PATH,ALTERNATE_RUNLOG_PATH]:
            try:
                os.system("rm -rf %s" % d)
                os.makedirs(d)
            except Exception:
                pass

    def tearDown(self):
        for d in [NON_DEFAULT_RUNLOG_PATH,ALTERNATE_RUNLOG_PATH]:
            try:
                os.system("rm -rf %s" % d)
            except Exception:
                pass

    def testScriptCompose(self):
        """
        Ensure that BashSystem.compose() creates a script using the content and optional comment kwargs.  Comments should be wrapped if larger than 60 chars.
        """
        bash = BashSystem()
        simplecontent = "script file content\nwith\nseveral\nlines\n"
        simplecomment = "script file comment"
        longcomment = """This is a fairly long comment that should easily be stretched way over eighty characters because it has like way more than that. 
We should be two comment lines in the bash script."""

        script = bash.compose(content=simplecontent)
        self.assertTrue(simplecontent in script, "Script does not contain content: \n%s" % script)

        script = bash.compose(content=simplecontent,comment=simplecomment)
        self.assertTrue(simplecontent in script, "Script does not contain content: \n%s" % script)
        self.assertTrue("# %s" % simplecomment in script, "Script does not contain comment: \n%s" % script)

        script = bash.compose(content=simplecontent,comment=longcomment)
        self.assertTrue(simplecontent in script, "Script does not contain content: \n%s" % script)
        self.assertTrue("# %s" % longcomment[0:51] in script, "Script does not contain comment: \n%s" % script)
        self.assertTrue("# %s" % longcomment[52:100] in script, "Script does not contain wrapped comment line: \n%s" % script)

    def testScriptFileWithDefaultRunLogger(self):
        """
        Ensure that BashSystem.makeScriptFile creates the expected scriptfile using the DefaultRunLogger
        """
        runlogger = DefaultRunLogger(pathname=NON_DEFAULT_RUNLOG_PATH)
        runid = runlogger.newRunId()

        bash = BashSystem(runlogger=runlogger)
        scriptfilepath = bash.makeScriptFile("hostname",runid=runid)
        self.assertTrue(os.path.exists(scriptfilepath),"Script file not created: %s" % scriptfilepath)
        self.assertTrue(scriptfilepath == os.path.join(NON_DEFAULT_RUNLOG_PATH,runid,"%s-%s%s" % (runid,"script",".sh")),"Incorrect script path: %s" % scriptfilepath)
        contents = open(scriptfilepath,"r").read()
        self.assertTrue("hostname" in contents,"Bad scriptfile contents: %s" % contents)

    def testMinimalExecute(self):
        """
        Execute a command with BashSystem.execute with no specified runid, stdoutfile, etc.
        """
        runlogger = DefaultRunLogger(pathname=NON_DEFAULT_RUNLOG_PATH)
        bash = BashSystem(runlogger=runlogger)

        outstr = "Stdout"
        errstr = "Stderr"
        cmd = "echo '%s' && echo '%s' >&2" % (outstr,errstr)
        runid = bash.execute(cmd)

        runlog = bash.runlogger.get(runid)
        self.assertTrue(runlog["cmd"] == cmd, "Incorrect command: %s" % runlog["cmd"])
        self.assertTrue(runlog["system"] == "hex.system.bashsystem.BashSystem", "Incorrect system: %s" % runlog["system"])
        self.assertTrue(runlog["runid"] == runid, "Incorrect runid: %s" % runlog["runid"])
        self.assertTrue(runlog["status"] == "COMPLETED", "Incorrect status: %s" % runlog["status"])
        self.assertTrue(runlog["result"] == "SUCCESS","Incorrect result: %s" % runlog["result"])
        stdout = open(runlog["stdoutfile"], "r").read()
        self.assertTrue(outstr in stdout, "Incorrect stdout: %s" % stdout)
        stderr = open(runlog["stderrfile"], "r").read()
        self.assertTrue(errstr in stderr, "Incorrect stderr: %s" % stderr)
        script = open(runlog["scriptfilepath"], "r").read()
        self.assertTrue(cmd in script, "Incorrect script contents: %s" % script)

    def testExecuteWithSpecifiedRunId(self):
        """
        Execute a command with BashSystem.execute with a specified runid.
        """
        runlogger = DefaultRunLogger(pathname=NON_DEFAULT_RUNLOG_PATH)
        bash = BashSystem(runlogger=runlogger)

        outstr = "Stdout"
        errstr = "Stderr"
        cmd = "echo '%s' && echo '%s' >&2" % (outstr,errstr)
        runid = "howdydoody"
        bash.execute(cmd,runid=runid)

        runlog = bash.runlogger.get(runid)
        self.assertTrue(runlog["runid"] == runid, "Incorrect runid: %s" % runid)
        self.assertTrue(runid in runlog["scriptfilepath"], "Script file path does not contain the runid: %s" % runlog["scriptfilepath"])
        self.assertTrue(runid in runlog["stdoutfile"], "Stdout file path does not contain the runid: %s" % runlog["stdoutfile"])
        self.assertTrue(runid in runlog["stderrfile"], "Stderr file path does not contain the runid: %s" % runlog["stderrfile"])

    def testExecuteWithSpecifiedRunIdStdoutStderr(self):
        """
        Execute a command with BashSystem.execute with a specified runid, stdoutfile, and stderrfile
        """
        runlogger = DefaultRunLogger(pathname=NON_DEFAULT_RUNLOG_PATH)
        bash = BashSystem(runlogger=runlogger)

        stdoutfile = os.path.join(ALTERNATE_RUNLOG_PATH,"stdout.out")
        stderrfile = os.path.join(ALTERNATE_RUNLOG_PATH,"stderr.err")

        outstr = "Stdout"
        errstr = "Stderr"
        cmd = "echo '%s' && echo '%s' >&2" % (outstr,errstr)
        runid = "howdydoody"
        bash.execute(cmd,runid=runid,stdoutfile=stdoutfile,stderrfile=stderrfile)

        runlog = bash.runlogger.get(runid)
        self.assertTrue(runlog["stdoutfile"] == stdoutfile, "Incorrect stdoutfile: %s" % runlog["stdoutfile"])
        self.assertTrue(runlog["stderrfile"] == stderrfile, "Incorrect stderrfile: %s" % runlog["stderrfile"])
        self.assertTrue(runlog["runid"] == runid, "Incorrect runid: %s" % runlog["runid"])

    def testLaunchWithLongRunningScript(self):
        """
        Execute a command with BashSystem.launch and a long running script.  Should take about 20 seconds.
        """
        runlogger = DefaultRunLogger(pathname=NON_DEFAULT_RUNLOG_PATH)
        bash = BashSystem(runlogger=runlogger)
        sleepytime = 20

        # Using an array of commands
        cmds = [
            "echo 'Starting...'",
            "sleep %d" % sleepytime,
            "echo 'Done.'"
        ]

        runid = bash.launch(cmds)

        # Make sure the initial information indicates that it's running
        runlog = bash.runlogger.get(runid)
        self.assertTrue(runlog["status"] == "RUNNING","Incorrect status: %s" % runlog["status"])
        self.assertTrue("result" not in runlog.keys(), "Runlog has a result: %s" % str("runlog"))

        # Wait for it...
        time.sleep(sleepytime)

        # Should be done by now.
        runlog = bash.runlogger.get(runid)
        self.assertTrue(runlog["status"] == "COMPLETED","Command not completed! \n%s" % str(runlog))
        self.assertTrue(runlog["result"] == "SUCCESS","Command failed!\n%s" % str(runlog))
