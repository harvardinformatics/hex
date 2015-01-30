"""
Created on Oct 10, 2014
Copyright (c) 2014
Harvard FAS Research Computing
All rights reserved.

@author: Aaron Kitzmiller
"""
import os,subprocess,socket,time
import tempfile
import datetime
from hex import DefaultFileLogger, Command, RunLog, getClassFromName

class Env(dict):
    """
    Dictionary that can be used to set environment variables in a runner
    """
    def prepend_path(self,path,value):
        """
        Prepends a path element to a PATH-like variable
        """
        if path not in self:
            self[path] = os.environ.get(path)
        if self[path] is None:
            self[path] = value
        else:
            self[path] = ':'.join(value,self[path])
                
            
              
class ShellRunner(object):
    """
    Runs a Command object and returns a result.  The result is where all the action
    happens.  
     
    Logger classes are used to record execution.
     
    Environment for the command execution can be set, including working directory.
    """
     
    def __init__(self,logpath=None,verbose=0,usevenv=False):
        
        logger = None
        if logpath is None:
            logpath = tempfile.mkdtemp("", "rcx")
            logger = DefaultFileLogger(pathname=logpath)
        elif logpath.startswith("mysql:"):
            raise Exception("MySQL logpath not supported yet")
        else:
            # Assume it's a file path
            logger = DefaultFileLogger(pathname=logpath)
            
        self.logger = logger
        self.verbose = verbose
        self.usevenv = usevenv
     
    def checkStatus(self,runlog=None,proc=None):
        """
        Checks the status of processes.  If proc parameter is set, uses proc.poll().
        Otherwise, if runlog is set, checks jobs using kill -0 <pid>. 
        sshs to remote host if necessary.
        
        Returns None if the process is still running.  Returns something otherwise.
        If proc is set, it will return it's return value (ie the exitcode). 
        """
        if proc is not None:
            exitcode = proc.poll()
            return exitcode
        else:
            thishostname = socket.gethostname().split('.',1)[0]
            checkcmd = ""
            if thishostname == runlog['hostname'] or thishostname == 'localhost':
                checkcmd = "kill -0 %d" % runlog['jobid']
            else:
                checkcmd = "ssh %s 'kill -0 %d'" % (runlog['hostname'],runlog['jobid'])
                
            devnull = open(os.devnull,'w')
            returnval = subprocess.call(checkcmd,shell=True,stdout=devnull,stderr=subprocess.STDOUT)
            if returnval == 0:
                return None
            else:
                return returnval
            
        
     
    def run(self,cmds,runhandler=None,runsetname=None,stdoutfile=None,stderrfile=None,logger=None):
        """
        Runs a Command and returns a RunHandler
        """
        if logger is None:
            logger = self.logger
        if runsetname is None:
            runsetname = logger.getRunsetName()
        if runhandler is None:
            runhandler = RunHandler(logger,runsetname)
            
        # cmds should be an array
        if not isinstance(cmds,list):
            cmds = [cmds]
         
        hostname = socket.gethostname().split('.',1)[0]
        pid = os.fork()
        if pid == 0:
            runset = []
            for cmd in cmds:
                
                # Prepare the command string using the Runner method
                cmdstring = self.getCmdString(cmd)
                
                # Get a tempfile stdout and stderr if they aren't specified
                if stdoutfile is None:
                    stdoutfile = logger.getStdOutFileName()
                if stderrfile is None:
                    stderrfile = logger.getStdErrFileName()                    
                stdout = open(stdoutfile,'w')
                stderr = open(stderrfile,'w')
        
                # Launch the process
                proc = subprocess.Popen(cmdstring,shell=True,stdout=stdout,stderr=stderr)
                starttime = datetime.datetime.now()
                runlog = RunLog( jobid=proc.pid,
                                 cmdstring=cmdstring,
                                 starttime=starttime,
                                 hostname=hostname,
                                 stdoutfile=stdoutfile,
                                 stderrfile=stderrfile,
                                 runner="%s.%s" % (self.__module__, self.__class__.__name__)
                )
            runset.append(runlog)
            if self.verbose > 0:
                print runlog
            logger.saveRunSet(runset, runsetname)
            os._exit(0)
        else:
            time.sleep(1)
                   
        return runhandler
      
      
    def getCmdString(self,cmd):
        """
        Returns the command string, using the Command.composeCmdString()
        """
        cmdstring = cmd.composeCmdString()
        if self.usevenv:
            if "VIRTUAL_ENV" in os.environ:
                cmdstring += "source %s/bin/activate && " % os.environ["VIRTUAL_ENV"]
            elif "CONDA_DEFAULT_ENV" in os.environ:
                cmdstring += "source activate %s &&" % os.environ["CONDA_DEFAULT_ENV"]
        return cmd.composeCmdString()
    
     
     
class RunHandler(object):
    """
    Result of a Runner.submit() or Runner.run().  Can be used to access
    the state and result of a running job via the RunSet
          
    If the RunSet only has a single Run record, then things like 
    RunHandler.stderr will return the standard error stream.
     
    """
    def __init__(self,logger,runsetname):
        self.cmds = []
        self.logger = logger
        self.runsetname = runsetname
        self.status = ''
             
             
         
    def getRunSet(self):
        """
        Return the run set via the logger and the runsetname
        """
        return self.logger.getRunSet(self.runsetname)
     
     
      
    def checkStatus(self,runlog=None):
        """
        Use runner to check the status for the given runlog.  Like with the 
        runner.checkStatus method, a return value of None means it is still 
        running and anything else is the "exit status"
        
        Calls setDone if the result is not None
        """
        if runlog is None:
            if hasattr(self,"proc") and hasattr(self,"runner") and self.proc and self.runner:
                return self.runner.checkStatus(proc=self.proc)
            else:
                runlog = self.getRunSet()[0]
                
        # If it has finished, return the exitstatus
        if "endtime" in runlog:
            return runlog["exitstatus"]              
            
        runner = None
        if hasattr(self,"runner"):
            runner = self.runner
        if not runner:
            cls = getClassFromName(runlog['runner'])
            runner = cls()
        result = runner.checkStatus(runlog=runlog)
        if result is not None:
            self.setDone(runlog, self.runsetname, exitstatus=result)
        return result
    
    
    def setDone(self,runlog,runsetname,exitstatus=None,endtime=None):
        """
        Sets the exitstatus and endtime in the runlog
        """
        if runlog is None:
            raise Exception("Need a runlog to setDone")
        if endtime is None:
            endtime = datetime.datetime.now()
        runlog['endtime'] = endtime
        if exitstatus is None:
            exitstatus = "unknown"
        runlog["exitstatus"] = exitstatus
        self.logger.saveRunSet([runlog],runsetname)
        self.status = "Completed"
        
    
    def wait(self):
        """
        Polls specified job until it is complete
        """        
        # Check for command completion with up to 20 sec delay between checks
        delay = [0,1]
        result = self.checkStatus()
        while result is None:
            time.sleep(delay[1])
            if delay[1] < 20:
                delay[0],delay[1] = delay[1], delay[0] + delay[1]
            result = self.checkStatus()
        
        return result           
         
         
    def getStdOut(self):
        """
        Get stdout stream handle
        """
        runset = self.getRunSet()
        return runset[0].getStdOut()
    
    
    def getStdErr(self):
        """
        Get stderr stream handle
        """
        runset = self.getRunSet()
        return runset[0].getStdErr()
    
    
    def getStdOutString(self):
        """
        Get the completed stdout string
        """
        self.wait()
        stdout = self.getStdOut()
        return ''.join(stdout.readlines())
    
    
    def getStdErrString(self):
        """
        Get the completed stderr string
        """
        self.wait()
        stderr = self.getStdErr()
        return ''.join(stderr.readlines())
    
    
    def getExitStatus(self):
        """
        Get the exitstatus value from the runlog.  This will call wait() until the process is finished.
        
        If you're connecting to a previously run process, this will return None.
        """
        self.wait()
        runlog = self.getRunSet()[0]
        return runlog["exitstatus"] 
    
    def __getattr__(self,attr):
        """
        Do the actual execution if something is requested (and execution is pending)
        """
             
        # If it's one of the usual suspects, then get the RunSet and return the 
        # value for the "default" Run (ie the first one)
        if attr in ['jobid','starttime','stderr','stderrstr','stdout','stdoutstr','exitstatus']:

            # Most of these won't work without a runset name
            if not hasattr(self,'runsetname'):
                return None
                            
            if attr in ['jobid','starttime']:
                runset = self.getRunSet()
                return runset[0][attr]
            
            if attr == 'stdout':
                return self.getStdOut()
            if attr == 'stderr':
                return self.getStdErr()
            
            if attr == 'stdoutstr':
                return self.getStdOutString()
            if attr == 'stderrstr':
                return self.getStdErrString()
            if attr == 'exitstatus':
                return self.getExitStatus()
            
                 
        return self.__dict__[attr]
     
