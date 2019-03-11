#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
RunLog - a record of a command line execution

@date      : 2017-06-20 16:08:43
@author    : Aaron Kitzmiller (aaron_kitzmiller@harvard.edu)
@version   : $Id$
@copyright : 2017 The Presidents and Fellows of Harvard College. All rights reserved.
@license   : GPLv2

"""
import os


class RunLog(dict):
    """
    Just a dictionary with some required fields
    """
    
    def __init__(self,**kwargs):
        self.required = ["jobid","hostname","scriptfilepath","interpreter","starttime","system"]
        for key in self.required:
            if key not in kwargs:
                raise Exception("Run log must have a %s key" % key)
        for k,v in kwargs.iteritems():
            self[k] = v
                           
    def getStdOutHandle(self):
        """
        Get a file handle for stdout
        """
        if "stdoutfile" not in self or self["stdoutfile"] == "" or not os.path.exists(self["stdoutfile"]):
            return None
        
        f = open(self["stdoutfile"],"r")
        return f
        
    def getStdErrHandle(self):
        """
        Get a file handle for stderr
        """
        if "stderrfile" not in self or self["stderrfile"] == "" or not os.path.exists(self["stderrfile"]):
            return None
        
        f = open(self["stderrfile"],"r")
        return f

    def getScriptHandle(self):
        """
        Get a handle for the script file
        """
        if "scriptfilepath" not in self or self["scriptfilepath"] == "" or not os.path.exists(self["scriptfilepath"]):
            return None
        
        f = open(self["scriptfilepath"],"r")
        return f
