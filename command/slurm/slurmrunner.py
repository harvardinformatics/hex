"""
Created on Oct 9, 2014
Copyright (c) 2014
Harvard FAS Research Computing
All rights reserved.

@author: Aaron Kitzmiller
"""
import subprocess,os,socket
import datetime,time
from command import ShellRunner,RunLog,RunHandler,Command,DefaultFileLogger
from command.slurm import SbatchCommand
from command.slurm.sbatch import SBATCH_NOSUBMIT_OPTIONS

class SlurmRunner(ShellRunner):
    """
    ShellRunner class that gets job ids instead of pids and uses squeue
    to determine status
    """
    def __init__(self,logger=DefaultFileLogger(),verbose=0,usevenv=False):
        super(self.__class__,self).__init__(logger=logger,verbose=verbose,usevenv=usevenv)

    def getSlurmStatus(self,jobid):
        checkcmd = "squeue -j %s --format=%%T -h" % jobid
        if self.verbose > 1: 
            print "checkcmd %s" % checkcmd
        p = subprocess.Popen(checkcmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        (out,err) = p.communicate()
        out = out.strip()
        err = err.strip()
        if self.verbose > 1:
            print "squeue out %s err %s" % (out,err)
        if out is not None and out != "":
            # It's still running
            return out
        else:
            # Get the result from sacct
            sacctcmd = "sacct -j %s.batch --format=State -n" % jobid
            p = subprocess.Popen(sacctcmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            (out,err) = p.communicate()
            out = out.strip()
            err = err.strip()
            if self.verbose > 1:
                print "sacct out is %s" % out
            return out
        
    def checkStatus(self,runlog=None,proc=None):
        """
        Checks the status of processes using squeue.
        Runlog must have a job id in it 
        """
        if runlog is None:
            raise Exception("Cannot checkStatus without runlog")
        
        # If it's a "help" or "usage" run, just use the parent checkStatus
        for option in SBATCH_NOSUBMIT_OPTIONS:
            if "--%s" % option in runlog["cmdstring"]:
                return super(self.__class__,self).checkStatus(runlog,proc)
       
        result = self.getSlurmStatus(runlog["jobid"]) 
        if result in ["CANCELLED","COMPLETED","FAILED","TIMEOUT","NODE_FAIL","SPECIAL_EXIT"]:
            return result
        else:
            return None
                 
    def getCmdString(self,cmd):
        """
        If the command parameter of the sbatch command is a Command object,
        it is converted into a string here.
        
        If it is an array, the commands are joined by newline into a string
        """
        if hasattr(cmd,"command") and isinstance(cmd.command, Command):
            cmd.command = cmd.command.composeCmdString()
            return super(self.__class__,self).getCmdString(cmd)
        elif isinstance(cmd,list):
            cmdarr = []
            for c in cmd:
                if hasattr(c,"command") and isinstance(c.command, Command):
                    c.command = c.command.composeCmdString()
                    cmdarr.append(c.command.composeCmdString())
                cmdarr.append(super(self.__class__,self).getCmdString(cmd))
            return "\n".join(cmdarr)
        else:
            return super(self.__class__,self).getCmdString(cmd)
                
            
            
        
    def run(self,cmds,runhandler=None,runsetname=None,stdoutfile=None,stderrfile=None,logger=None):
        """
        Runs a Command and returns a RunHandler.
        Mostly calls parent run 
        """
        if logger is None:
            logger = self.logger
        if runsetname is None:
            runsetname = logger.getRunsetName()
        if runhandler is None:
            runhandler = RunHandler(logger,runsetname)
            
            
        if not isinstance(cmds,list):
            cmds = [cmds]
            
                    
        hostname = socket.gethostname().split('.',1)[0]
        
        pid = os.fork()
        if pid == 0:
            for cmd in cmds:
                
                # For options like "help" and "usage", the parent method should be called if the value is True
                for option in SBATCH_NOSUBMIT_OPTIONS:
                    if cmd.getArgValue(option):
                        super(self.__class__,self).run(cmd,runhandler,runsetname,stdoutfile=stdoutfile,stderrfile=stderrfile,logger=logger)
                        os._exit(0)
                
                if isinstance(cmd,SbatchCommand):
                    if cmd.output:
                        stdoutfile = cmd.output
                    else:
                        stdoutfile = logger.getStdOutFileName()
                        cmd.output = stdoutfile
                    if cmd.error:
                        stderrfile = cmd.error
                    else:
                        stderrfile = logger.getStdErrFileName()
                        cmd.error = stderrfile
                        
                cmdstring = self.getCmdString(cmd)                                      
                        
                # Since stdout and stderr are taken care of by the sbatch script,
                # we use subprocess.PIPE here                    
                proc = subprocess.Popen(cmdstring,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                (out,err) = proc.communicate()
                if err:
                    raise Exception("sbatch submission failed %s" % err)
                
                jobid = out.split()[-1]
                
                starttime = datetime.datetime.now()
                runset = []
                runlog = RunLog( jobid=jobid,
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
            # Wait until the runset file has been written
            ready = False
            while not ready:
                time.sleep(2)
                try:
                    logger.getRunSet(runsetname)
                    ready = True
                except Exception:
                    pass
        return runhandler    

