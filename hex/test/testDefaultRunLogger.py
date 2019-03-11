# -*- coding: utf-8 -*-

"""
Tests for the DefaultRunLogger

@date      : 2017-07-18 12:06:51
@author    : Aaron Kitzmiller (aaron_kitzmiller@harvard.edu)
@version   : $Id$
@copyright : 2017 The Presidents and Fellows of Harvard College. All rights reserved.
@license   : GPLv2

"""
import unittest, os
from hex.runlog import DefaultRunLogger,DEFAULT_RUNLOG_PATH,RunLog
from datetime import datetime


NON_DEFAULT_RUNLOG_PATH = "/tmp/runlogs"


@unittest.skipIf(os.path.exists(DEFAULT_RUNLOG_PATH) and len(os.listdir(DEFAULT_RUNLOG_PATH)) > 0, "You have runlogs in %s.  Clear these out before running this test." % DEFAULT_RUNLOG_PATH)
class DefaultRunLoggerTest(unittest.TestCase):

    def cleanDirectories(self):
        for d in [NON_DEFAULT_RUNLOG_PATH,DEFAULT_RUNLOG_PATH]:
            if d.strip() == "" or d.strip() == "/":
                raise Exception("What are you thinking?")
            os.system("rm -rf %s" % d)

    def setUp(self):
        self.cleanDirectories()

    def tearDown(self):
        self.cleanDirectories()

    def testNewRunId(self):
        """
        Create a new run id without the command string using the DefaultRunLogger
        """
        runlogger = DefaultRunLogger()
        runid = runlogger.newRunId()
        self.assertTrue('tmp' in runid, "Weird run id %s" % runid)

    def testNewRunIdCmd(self):
        """
        Create a new run id with a command string using the DefaultRunLogger
        """
        runlogger = DefaultRunLogger()
        cmd = "sed"
        runid = runlogger.newRunId(cmd)
        self.assertTrue(cmd in runid,"Runid should include %s: %s" % (cmd,runid))

        cmd = "asdfghjklm"
        runid = runlogger.newRunId(cmd)
        self.assertFalse(runid.startswith(cmd),"Runid should not include all of %s: %s" % (cmd,runid))
        self.assertTrue(cmd[0:8] in runid,"Runid should include %s: %s" % (cmd[0:8],runid))

    def testGetRunLogById(self):
        """
        Save and retrieve a runlog by id using default runlog path with the DefaultRunLogger
        """
        runlogger = DefaultRunLogger()
        runlogdata = {
            "jobid"             : 10,
            "hostname"          : "localhost",
            "scriptfilepath"    : "/path/to/script",
            "interpreter"       : "/bin/bash",
            "starttime"         : datetime(2017,1,1),
            "system"            : "BashSystem",
        }
        runlog = RunLog(**runlogdata)
        runid = runlogger.save(runlog)

        # Make sure the path is created as expected
        runlogpath = runlogger.getRunLogPath(runid)
        self.assertTrue(os.path.exists(runlogpath),"Expected runlog path does not exist!")

        # Make sure the data retrieved is correct
        retrieved = runlogger.get(runid)
        for k,v in runlogdata.items():
            self.assertTrue(retrieved[k] == v,"Run log value for %s is incorrect: %s" % (k,str(v)))

    def testRunLogSavePath(self):
        """
        Save run log to specified path using the DefaultRunLogger
        """
        runlogger = DefaultRunLogger(pathname=NON_DEFAULT_RUNLOG_PATH)
        runlogdata = {
            "jobid"             : 10,
            "hostname"          : "localhost",
            "scriptfilepath"    : "/path/to/script",
            "interpreter"       : "/bin/bash",
            "starttime"         : datetime(2017,1,1),
            "system"            : "BashSystem",
        }
        runlog = RunLog(**runlogdata)
        runid = runlogger.save(runlog)

        # Make sure the path is created as expected
        runlogpath = runlogger.getRunLogPath(runid)
        self.assertTrue(os.path.exists(runlogpath),"Expected runlog path does not exist!")
        self.assertTrue(runlogpath.startswith(NON_DEFAULT_RUNLOG_PATH),"Runlog path is not using the specified root (%s): %s" % (NON_DEFAULT_RUNLOG_PATH,runlogpath))

        # Make sure the data retrieved is correct
        retrieved = runlogger.get(runid)
        for k,v in runlogdata.items():
            self.assertTrue(retrieved[k] == v,"Run log value for %s is incorrect: %s" % (k,str(v)))

    def testCreatePathsByRunId(self):
        """
        Create script, stdout, stderr, and runlog paths for a given runid using the DefaultRunLogger
        """
        runlogger = DefaultRunLogger(pathname=NON_DEFAULT_RUNLOG_PATH)
        runid = runlogger.newRunId()
        runlogpath = runlogger.getRunLogPath(runid)
        self.assertTrue(runlogpath == os.path.join(NON_DEFAULT_RUNLOG_PATH,runid,"%s-%s%s" % (runid,"runlog",runlogger.suffix)))

        scriptpath = runlogger.getScriptPath(runid,".sh")
        self.assertTrue(scriptpath == os.path.join(NON_DEFAULT_RUNLOG_PATH,runid,"%s-%s%s" % (runid,"script",".sh")), "Incorrect scriptpath %s" % scriptpath)

        stdout = runlogger.getStdOutPath(runid)
        self.assertTrue(stdout == os.path.join(NON_DEFAULT_RUNLOG_PATH,runid,"%s-%s%s" % (runid,"stdout",".out")), "Incorrect stdout file %s" % stdout)

        stderr = runlogger.getStdErrPath(runid)
        self.assertTrue(stderr == os.path.join(NON_DEFAULT_RUNLOG_PATH,runid,"%s-%s%s" % (runid,"stderr",".err")), "Incorrect stderr file %s" % stderr)
