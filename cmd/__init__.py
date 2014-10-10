"""
Created on Sep 24, 2014
Copyright (c) 2014
Harvard FAS Research Computing
All rights reserved.

@author: Aaron Kitzmiller

bowtie2project = Project(name="bowtie2project")
bowtie2project.home = ""
bowtie2project.inputpaths.append("/data/sequences1")
bowtie2project.inputpaths.append("/data/sequences2")



bowtiecmd = Command("bowtie2",x="/path/to/index",U="/path/to/unpaired")
dockercmd = Command("docker","run","bowtie:1.0")
slurmcmd  = Command("sbatch",n="4",N="1",contiguous=True,scriptname="docker-bowtie2.sbatch")

result = ShellRunner.run(slurmcmd).run(dockercmd).run(bowtiecmd)
print result.paramsOk()
> True
print result.cmdstring
> rcx.py sbatch docker-bowtie2.sbatch
print slurmcmd.script
> #/bin/bash
> #SBATCH -n 4
> #SBATCH -N 1
> #SBATCH --contiguous
> rcx.py --run-project testproject --run-logdir mydir docker run bowtie:1.0 rcx.py --run-project testproject --run-logdir mydir bowtie2 -x /path/to/index -U /path/to/unpaired

"""
import os,sys,subprocess,socket,time
import tempfile
import re
import datetime

import yaml
from string import Template

import json

DEFAULT_PDEF_PATH='../conf'

def getClassFromName(classname):
    parts = classname.split('.')
    module = ".".join(parts[:-1])
    m = __import__( module )
    for comp in parts[1:]:
        m = getattr(m, comp)            
    return m

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
            self['runner'] = "cmd.ShellRunner"
                
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
            


class ParameterDef(object):
    """
    Command parameter definition
    """
    def __init__(self,name=None,required='no',switches=[],pattern=None,description="",validator='cmd.validators.StringValidator',order=0):
        if name is None:
            raise Exception("ParameterDef must have a name")
        if pattern is None:
            raise Exception("ParameterDef must have a pattern")
        self.name = name
        self.required = required
        self.switches = switches
        self.pattern = pattern
        self.description = description
        self.order = order
        validator = getClassFromName(validator)
        self.validator = validator()
        
    def isValid(self,value):
        """
        Use specified validator object to check value
        """
        return self.validator.isValid(value)
        

 
class Command(object):
    """
    Represents a command line.  If composed with ParameterDefs, this can be used to
    validate and interrogate arguments.  It can also be used with a plain string
    command or an array of command elements.
    """
    @classmethod
    def fetch(cls,name,path=DEFAULT_PDEF_PATH):
        """
        Create a Command object using a JSON definition file
        """
        if not name.endswith('.json'):
            name = name + '.json'
        pardata = {}
        with open(os.path.join(path,name),'r') as pdeffile:
            pardata = json.load(pdeffile)
        if pardata is None:
            raise Exception("No command defined in %s" % path)
        if "cmdclass" not in pardata:
            pardata["cmdclass"] = "cmd.Command"
        cls = getClassFromName(pardata["cmdclass"])
        cmd = cls()
        cmd.name        = pardata["name"]
        cmd.bin         = pardata["bin"]
        cmd.version     = pardata["version"]
        cmd.description = pardata["description"]
        
        parameterdefs = []
        for pdef in pardata["parameterdefs"]:
            parameterdefs.append(ParameterDef(**pdef))
        cmd.setParameterDefs(parameterdefs)
        return cmd
        
    def __init__(self,*args,**kwargs):
        """
        Initialize the command object.  There are multiple modes:
         
            Command("echo","junk","-n")     #array of strings mode.  Run without shell interpolation
            Command("echo","junk",n=True)   #arguments plus parameter switch
             
            echo = Command.fetch("/definition/of/echo.json")
            echo.e=True                     #From definition, using parameter switch
             
            parameters = dict("n": "1")
            Command("echo",junkstring,**parameters)  # Dict of parameters  
             
            Command(["echo","junk"])        #An array.  Run without shell interpolation           
                    
        """
         
        #### TODO gotta check for the existence of parameter definitions.  If there 
        #### are definitions, should require keyword args for named parameters
         
        if kwargs is None:
            """
            We have an array of items, probably strings
            """
            if args is None:
                raise Exception("Can't create an empty command")
             
            if len(args) == 1:
                if isinstance(args[0],basestring):
                    """
                    Probably just a single command string
                    """
                    self.cmdstring = args[0]
                elif isinstance(args[0],list):
                    self.cmdarray = args[0]
                else:
                    raise Exception("Single argument Command should be a string or an array")
            else:
                """
                Treat them as an array if they are all strings
                """
                # Make sure they're all strings
                for a in args:
                    if not isinstance(a,basestring):
                        raise Exception("Not sure what you're doing here")
                self.cmdarray = args
        else:
            """
            Some keyword args were passed in
            """
            if len(args) > 0:
                """
                Put them on the command array
                """
                self.cmdarray = args
             
            for k,v in kwargs.iteritems():
                self.setArgValue(k,v)
             
                 
     
    def composeCmdString(self):
        """
        Constructs the command string from the various elements.  If the command 
        has arguments they are concatenated first, then key-value pairs are added
        """
        if hasattr(self,"cmdstring"):
            return self.cmdstring
        cmdstring = ""
        if hasattr(self,"cmdarray") and len(self.cmdarray)  > 0:
            cmdstring += " ".join(self.cmdarray)
        if hasattr(self,"cmdparametervalues"):
            if not hasattr(self,"parameterdefs"):
                for k,v in self.cmdparametervalues.iteritems():
                    if not k.startswith("-"):
                        if len(k) == 1:
                            k = "-" + k
                        else:
                            k = "--" + k
                    if v == False:
                        continue
                    if v == True:
                        cmdstring += " %s" % k
                    else:
                        cmdstring += " %s=%s" % (k,v)
            else:
                # This is the branch for commands defined by parameter defs
                # Tool name should be in the "bin" attribute                
                if hasattr(self,"bin"):
                    cmdstring = self.bin
                else:
                    raise Exception("Specified command must have a 'bin' attribute.")
                
                # Determines if the argument pattern is an optional one
                optionalargre = re.compile("\?.+?\?")
                
                # Determines if the argument pattern has quoting of the <VALUE>
                quotecheckre = re.compile("(\S)<VALUE>(\S)")                
                
                # Go through the parameter defs in order and 
                # for any parameter with a value, substitute the value into the 
                # "pattern"
                
                # Sort the parameterdef keys based on pdef.order
                sortednames = sorted(self.parameterdefs.iterkeys(),key=lambda name: int(self.parameterdefs[name].order))
                
                for pname in sortednames:
                    pdef = self.parameterdefs[pname]
                    if pname in self.cmdparametervalues:
                        value = self.cmdparametervalues[pname]
                        
                        if value == False:
                            continue
                        
                        # If <VALUE> is surrounded by something (e.g. single quotes)
                        # then we should make sure that char is escaped in the value
                        quotestring = None
                        match = quotecheckre.search(pdef.pattern)
                        if match is not None:
                            if len(match.groups()) == 2:
                                if match.group(1) == match.group(2):
                                    quotestring = match.group(1)
                                    
                        # Do some courtesy escaping
                        if isinstance(value,basestring) and quotestring is not None:
                            # Remove existing escapes
                            value = value.replace("\\" + quotestring,quotestring)
                            # Escape the quote
                            value = value.replace(quotestring,"\\" + quotestring)
                            
                        
                        # Substitute the value into the pattern
                        if optionalargre.search(pdef.pattern) is not None:
                            
                            # This is the case of a switch with an optional argument
                            if value == True:
                                # Adding the switch with no argument
                                cmdstring += " %s" % optionalargre.sub("",pdef.pattern)
                            else:
                                # Remove the question marks and substitute the VALUE
                                cmdstring += " %s" % pdef.pattern.replace("?","").replace("<VALUE>",value)
                                
                        else:
                            if value == True:
                                cmdstring += " %s" % pdef.pattern
                            else:
                                cmdstring += " %s" % pdef.pattern.replace("<VALUE>",value)
                                                    
        return cmdstring.encode('ascii','ignore')
         
     
     
    def setArgValue(self,arg,value):
        """
        Sets arg value, checking against Parameters if they exist
        """
        if not hasattr(self,"cmdparametervalues"):
            self.cmdparametervalues = {}
         
        if hasattr(self,"parameterdefs"):
            if arg not in self.parameterdefs:
                raise Exception("Parameter %s is not valid for this command" % arg)
             
        self.cmdparametervalues[arg] = value    
         
    def getParameterDef(self,key):
        """
        Finds a matching parameter def based on name or switch
        """
        if key in self.parameterdefs:
            return self.parameterdefs[key]
        else:
            for pdef in self.parameterdefs:
                switches = pdef.switches
                if key in switches:
                    return pdef
            return None
        
    
    def setParameterDefs(self,parameterdefs):
        """
        Setup name-keyed parameter list
        """
        self.parameterdefs = {}
        for pdef in parameterdefs:
            self.parameterdefs[pdef.name] = pdef
        
              
    def isValid(self):
        """
        Base class validator just checks parameter validations if 
        Parameter array is set
        """
        if hasattr(self,"parameterdefs"):
            self.validationmsgs = []
            for k,v in self.cmdparametervalues.iteritems():
                msg = self.parameterdefs[k].isValid(v)
                if msg:
                    self.validationmsgs.append(msg)
            if len(self.validationmsgs) > 0:
                return False
            else:
                return True
        else:
            return True
        
        
    def __dir__(self):
        keys = self.__dict__.keys()
        if "parameterdefs" in self.__dict__:
            keys = list(set(keys + self.parameterdefs.keys()))
        return sorted(keys)
        
    
    def __getattr__(self,name):
        if "parameterdefs" in self.__dict__ and name in self.parameterdefs:
            if name in self.cmdparametervalues:
                return self.cmdparametervalues[name]
            else:
                return None
        else:
            return self.__dict__[name]
    
    def __setattr__(self,name,value):
        if "parameterdefs" in self.__dict__ and name in self.parameterdefs:
            self.setArgValue(name, value)
        else:
            self.__dict__[name] = value
                
 
             
# class ScriptCommand(Command):
#     """
#     Command that is run as a script fed to an interpreter
#     """
#     def __init__(self,bin,*args,**kwargs):
#         self.bin = bin
#         super(Command,self).__init__(args,kwargs)
#         
#     def composeCmdString(self):
#         """
#         Writes out a script and returns bin script command
#         """
#         pass
#             
#   
#       

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
     
    def __init__(self,logger=DefaultFileLogger(),verbose=0,usevenv=False):
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
            
     
     
    def run(self,cmd,runhandler=None,runsetname=None,stdoutfile=None,stderrfile=None,logger=None):
        """
        Runs a Command and returns a RunHandler
        """
        if logger is None:
            logger = self.logger
        if runsetname is None:
            runsetname = logger.getRunsetName()
        if runhandler is None:
            runhandler = RunHandler(logger,runsetname)
        if isinstance(cmd,basestring):
            cmd = Command(cmd)
        runhandler.setCmd(cmd,runner=self,stdoutfile=stdoutfile,stderrfile=stderrfile)
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
    

     
    def execute(self,cmd,runsetname,stdoutfile=None,stderrfile=None,logger=None):
        """
        Method that actually executes the Command(s).
        """
        if logger is None:
            logger = self.logger
        if stdoutfile is None:
            stdoutfile = logger.getStdOutFileName()
        if stderrfile is None:
            stderrfile = logger.getStdErrFileName()
             
        stdout = open(stdoutfile,'w')
        stderr = open(stderrfile,'w')
         
        hostname = socket.gethostname().split('.',1)[0]
        pid = os.fork()
        if pid == 0:
            proc = subprocess.Popen(cmd,shell=True,stdout=stdout,stderr=stderr)
            starttime = datetime.datetime.now()
            runset = []
            runlog = RunLog( jobid=proc.pid,
                             cmdstring=cmd,
                             starttime=starttime,
                             hostname=hostname,
                             stdoutfile=stdoutfile,
                             stderrfile=stderrfile,
                             runner="%s.%s" % (self.__module__, self.__class__.__name__)
            )
            runset.append(runlog)
            if self.verbose > 0:
                print runlog
        #print "Path is %s Runset name is %s" % (logger.pathname, runsetname)
            logger.saveRunSet(runset, runsetname)
            os._exit(0)
        else:
            time.sleep(1)
        return None
     
     
class RunHandler(object):
    """
    Result of a Runner.submit() or Runner.run().  Can be used to access
    the state and result of a running job via the RunSet
     
    Actual execution is deferred until this object is created and some
    thing is asked for.  This allows run() and submit() to be chained into
    a series of commands.
     
    If the RunSet only has a single Run record, then things like 
    RunHandler.stderr will return the standard error stream.
     
    """
    def __init__(self,logger,runsetname):
        self.cmds = []
        self.logger = logger
        self.runsetname = runsetname
        self.status = ''
             
    def setCmd(self,cmd,runner=ShellRunner(),stdoutfile=None,stderrfile=None):

        self.cmds.append((cmd,runner,stdoutfile,stderrfile))
     
    def run(self,cmd,addrcx=True,runner=ShellRunner(),stdoutfile=None,stderrfile=None):
        """
        This gets called when you chain stuff together.  The runner gets rcx.py set
        so that it will be called when the application is run.
        """
        self.cmds.append((cmd,runner,stdoutfile,stderrfile))
        return self
         
    def doRun(self):
        """
        This actually executes the code using the first runner in the list.  If there is 
        an array of command / runner /stdoutfile / stderrfile tuples, the command strings are chained together.
        """
        if len(self.cmds) == 0:
            raise Exception("Nothing to run")
        
        (command,runner,stdoutfile,stderrfile) = self.cmds.pop(0)
        self.runner = runner
        cmdstring = runner.getCmdString(command)
        
        for record in self.cmds:
            """
            Combine the runner / cmd combos into a single command string
            """
            cmdstring += "rcx.py --rcx-runner=%s --rcx-runsetname=%s --rcx-runsetpath=%s " % \
                         ( record[1].__class__.__name__, self.runsetname, self.logger.pathname)
            if record[2] is not None and record[2] != "":
                cmdstring += "--rcx-stdoutfile='%s' " % record[2]
            if record[3] is not None and record[3] != "":
                cmdstring += "--rcx-stderrfile='%s' " % record[3]
            cmdstring += record[1].getCmdString(record[0])
            
        self.status = 'Running'
        self.proc = runner.execute(cmdstring,runsetname=self.runsetname,stdoutfile=stdoutfile,stderrfile=stderrfile)
        self.status = 'Completed'
             
         
    def getRunSet(self):
        """
        Return the run set via the logger and the runsetname
        """
        return self.logger.getRunSet(self.runsetname)
     
     
      
    def checkStatus(self,runlog=None):
        if runlog is None:
            if self.proc and self.runner:
                return self.runner.checkStatus(proc=self.proc)
            else:
                runlog = self.getRunSet()[0]
        runner = self.runner
        if not runner:
            cls = getClassFromName(runlog['runner'])
            runner = cls()
        return runner.checkStatus(runlog=runlog)
    
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
    
    
    def getExitCode(self):
        """
        Get the exit code.  This only works if you're using Runners in the current
        process since it requires the subprocess.popen result.  
        
        If you're connecting to a previously run process, this will return None.
        """
        if not self.proc:
            return None
        else:           
            return self.wait()
                
    
    def __getattr__(self,attr):
        """
        Do the actual execution if something is requested (and execution is pending)
        """
        if self.status not in ['Running','Completed']:
            self.doRun()
             
        # If it's one of the usual suspects, then get the RunSet and return the 
        # value for the "default" Run (ie the first one)
        if attr in ['jobid','starttime','stderr','stderrstr','stdout','stdoutstr','exitcode']:
            if attr == 'exitcode':
                return self.getExitCode()

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
            
                 
        return self.__dict__[attr]
     
