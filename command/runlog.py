"""
Created on Oct 10, 2014
Copyright (c) 2014
Harvard FAS Research Computing
All rights reserved.

@author: Aaron Kitzmiller
"""
import os
import tempfile
import datetime

import yaml


class RunLog(dict):
    """
    Just a dictionary with some required fields
    """
    
    def __init__(self,**kwargs):
        self.required = ['jobid','hostname','cmdstring','starttime']
        for key in self.required:
            if key not in kwargs:
                raise Exception('Run log must have a %s key' % key)
        for k,v in kwargs.iteritems():
            self[k] = v
            
        if 'runner' not in kwargs:
            self['runner'] = "command.ShellRunner"
                
    def getStdOut(self):
        """
        Get a file handle for stdout
        """
        if 'stdoutfile' not in self or self['stdoutfile'] == "" or not os.path.exists(self['stdoutfile']):
            return None
        
        f = open(self['stdoutfile'],'r')
        return f
        
    def getStdErr(self):
        """
        Get a file handle for stderr
        """
        if 'stderrfile' not in self or self['stderrfile'] == "" or not os.path.exists(self['stderrfile']):
            return None
        
        f = open(self['stderrfile'],'r')
        return f
        
            
                
        
class FileLogger(object):
    """
    Logs process details to a directory
    """
    def __init__(self,pathname):
        self.pathname = pathname
        self.dateFormatString = "%Y-%m-%d %H:%M:%S"
        
        
    def getRunSet(self,runsetname):
        """
        Reads the runset from a yaml file and returns
        """
        runsetfilename = os.path.join(self.pathname,runsetname)
        runsetfilename += ".yaml"
        
        result = []
        
        with open(runsetfilename,'r') as runsetfile:
            runset = yaml.safe_load(runsetfile)
            for runlog in runset:
                for key in ['starttime','endtime']:
                    if key in runlog:
                        runlog[key] = datetime.datetime.strptime(runlog[key],self.dateFormatString)
                result.append(RunLog(**runlog))
        return result
  
    def saveRunSet(self,runset,runsetname):
        """
        Saves RunSet in yaml form
        """
        
        data = []
        for runlog in runset:
            for key in ['starttime','endtime']:
                if key in runlog:
                    runlog[key] = runlog[key].strftime(self.dateFormatString)
            #print runlog
            d = dict((k,v) for k,v in runlog.iteritems())
            data.append(d)
            
        runsetfilename = os.path.join(self.pathname,runsetname)
        runsetfilename += ".yaml"
        with open(runsetfilename,'w') as runsetfile:
            yaml.dump(data,runsetfile,width=1000)
            runsetfile.flush()
            os.fsync(runsetfile)
            
        return runsetfilename
            
        
            
class DefaultFileLogger(FileLogger):
    """
    Logs process details to /tmp
    """
    def __init__(self,pathname=None):
        if pathname is None:
            pathname = tempfile.mkdtemp("", "rcx")
        super(DefaultFileLogger,self).__init__(pathname)
        
    def getStdOutFileName(self):
        """
        Returns a temp file name for stdout
        """
        f = tempfile.NamedTemporaryFile(mode='w',suffix='.stdout', dir=self.pathname,delete=False)
        f.close()
        return f.name
    
    def getStdErrFileName(self):
        """
        Returns a temp file name for stderr
        """
        f = tempfile.NamedTemporaryFile(mode='w',suffix='.stderr', dir=self.pathname,delete=False)
        f.close()
        return f.name
    
    def getRunsetName(self):
        """
        Returns a temp file name for a runset file
        """
        f = tempfile.NamedTemporaryFile(mode='w',dir=self.pathname,delete=False)
        f.close()
        return os.path.basename(f.name)
        
               
               
                
class ProjectFileLogger(FileLogger):
    """
    Uses a standard project path and naming convention
    """
    def __init__(self,projectroot):
        pathname = os.path.join(projectroot,'log','runsets')
        if not os.path.exists(pathname):
            os.makedirs(pathname)
        super(ProjectFileLogger,self).__init__(pathname)
