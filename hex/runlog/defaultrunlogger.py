#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
DefaultRunLogger

| Stores run logs as individual json documents in a hidden home directory, ~/.hex/runlogs.
| File names are generated via tempfile, using the first 3-5 chars of the command being run.

@date      : 2017-06-21 10:47:02
@author    : Aaron Kitzmiller (aaron_kitzmiller@harvard.edu)
@version   : $Id$
@copyright : 2017 The Presidents and Fellows of Harvard College. All rights reserved.
@license   : GPLv2

"""
import os, re, logging
import json
import tempfile
from datetime import datetime
from hex.runlog import RunLog

DEFAULT_RUNLOG_PATH = os.path.expanduser("~/.hex/runlogs")

logger = logging.getLogger("hex")


class DefaultRunLogger(object):
    """
    Saves RunLogs as json documents in ~/.hex/runlogs/<runid> by default
    """
    def __init__(self,pathname=DEFAULT_RUNLOG_PATH):
        self.dateFormatString = "%Y-%m-%d %H:%M:%S"
        self.suffix = ".json"
        self.pathname = pathname

        if not os.path.exists(self.pathname):
            os.makedirs(self.pathname)

    def getRunPath(self,runid,resource,suffix):
        """
        Get a path name based on the resource and suffix.

        Resource can be something like "runlog","stdout","script", etc.
        """
        filename = "%s-%s%s" % (runid,resource,suffix)
        return os.path.join(self.pathname,runid,filename)

    def getRunLogPath(self,runid):
        """
        Convert a run id into a RunLog file path
        Joins self.pathname, runid, and the suffix (.json)
        """
        return self.getRunPath(runid,"runlog",self.suffix)

    def getScriptPath(self,runid,suffix):
        """
        Convert a run id into a script path
        Joins self.pathname, runid, runid+script+suffix
        """
        return self.getRunPath(runid,"script",suffix)

    def getStdOutPath(self,runid,suffix=".out"):
        """
        Convert a runid into a stdout filename
        """
        return self.getRunPath(runid,"stdout",suffix)

    def getStdErrPath(self,runid,suffix=".err"):
        """
        Convert a runid into a stderr filename
        """
        return self.getRunPath(runid,"stderr",suffix)

    def newRunId(self,cmd=None):
        """
        Create a unique run id.  Uses tempfile to create a directory in the path.

        If cmd is set, it will use the first 3-8 chars ([a-zA-Z_0-9-])
        as part of the directory name.
        """
        prefix = "tmp"
        if cmd is not None:
            match = re.search(r"([a-zA-Z_0-9-]{3,8})",cmd)
            if match:
                prefix = match.group(0)
        tname = tempfile.mkdtemp(prefix=prefix,dir=self.pathname)

        runid = os.path.split(tname)[1]

        return runid

    def get(self,runid):
        """
        Reads the RunLog from a json file and returns
        """
        runlogpath = self.getRunLogPath(runid)

        with open(runlogpath,"r") as f:
            runlogdata = json.load(f)
            if runlogdata is None:
                raise Exception("Unable to load runlog from %s" % runlogpath)
            for key in ["starttime","endtime"]:
                if key in runlogdata:
                    runlogdata[key] = datetime.strptime(runlogdata[key],self.dateFormatString)
        runlog = RunLog(**runlogdata)
        return runlog

    def save(self,runlog):
        """
        Saves RunLog to a json file
        """
        if "runid" not in runlog or runlog["runid"] is None or runlog["runid"].strip() == "":
            runid = self.newRunId(runlog.get("cmd"))
            runlog["runid"] = runid

        for key in ["starttime","endtime"]:
            if key in runlog:
                runlog[key] = runlog[key].strftime(self.dateFormatString)

        runlogfile = self.getRunLogPath(runlog["runid"])

        with open(runlogfile,"w") as f:
            json.dump(runlog,f,indent=4)

        return runlog["runid"]
