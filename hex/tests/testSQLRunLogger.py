# -*- coding: utf-8 -*-

"""
Tests for the SQLRunLogger

@date      : 2017-07-18 12:06:51
@author    : Meghan Porter-Mahoney (mportermahoney@g.harvard.edu)
@version   : $Id$
@copyright : 2017 The Presidents and Fellows of Harvard College. All rights reserved.
@license   : GPLv2

"""
import unittest, os, json
from hex.runlog import SQLRunLogger, RunLog
from datetime import datetime


class SQLRunLoggerTest(unittest.TestCase):

    def testSave(self):
        """
        test logging to sqllite with sqlrunlogger
        """
        runlogger = SQLRunLogger()
        runlogdata = {
            "jobid"             : 10,
            "hostname"          : "localhost",
            "scriptfilepath"    : "/path/to/script",
            "interpreter"       : "/bin/bash",
            "starttime"         : datetime(2017,1,1),
            "system"            : "BashSystem",
            "cmd"               : None,
            "endtime"         : datetime(2017,1,1),
            "stdoutfile"        : None,
            "stderrfile"        : None,
            "result"            : None,
            "status"            : None
        }
        runlog = RunLog(**runlogdata)
        runlogger.save(runlog)
        row = runlogger.get_row(runlog['runid'])
        row.pop('id', None) # remove id to compare
        self.assertTrue(row == runlog,"Sql row different from runlog ROW: %s RUNLOG: %s" %
                (json.dumps(row), json.dumps(runlog)))
