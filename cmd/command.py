"""
Created on Oct 10, 2014
Copyright (c) 2014
Harvard FAS Research Computing
All rights reserved.

@author: Aaron Kitzmiller
"""

import os
import re

import json

from cmd import DEFAULT_PDEF_PATH, getClassFromName


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
                
