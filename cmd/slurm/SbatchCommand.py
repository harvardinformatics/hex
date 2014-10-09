"""
Created on Oct 9, 2014
Copyright (c) 2014
Harvard FAS Research Computing
All rights reserved.

@author: Aaron Kitzmiller
"""
import re, os
import tempfile

from cmd import Command

class SbatchCommand(Command):
    """
    Modifications specific to Sbatch, including script generation
    and setting dependencies
    """
    def __init__(self,scriptpath="./"):
        """
        Set a script path, so that *.sbatch scripts can be written.  Default is cwd.
        """
        self.scriptpath = scriptpath
        
    def composeCmdString(self):
        cmdstring = ""
        
        # Determines if the argument pattern is an optional one
        optionalargre = re.compile("\?.+?\?")
        
        # Determines if the argument pattern has quoting of the <VALUE>
        quotecheckre = re.compile("(\S)<VALUE>(\S)")                
        
        # Go through the parameter defs in order and 
        # for any parameter with a value, substitute the value into the 
        # "pattern"
        
        # Sort the parameterdef keys based on pdef.order
        sortednames = sorted(self.parameterdefs.iterkeys(),key=lambda name: int(self.parameterdefs[name].order))
        scriptname = None
        commands = []
        for pname in sortednames:
            pdef = self.parameterdefs[pname]
            if pname in self.cmdparametervalues:
                value = self.cmdparametervalues[pname]
                
                if value == False:
                    continue
                
                # Process scriptname
                if pname == "scriptname":
                    scriptname = value
                    continue
                
                # Process command(s)
                if pname == "command":
                    if isinstance(value,basestring):
                        commands.append(value)
                    else:
                        if not isinstance(value,list):
                            value = [value]
                        for command in value:
                            if isinstance(command,Command):
                                commands.append(command.composeCmdString)
                            elif isinstance(command,basestring):
                                commands.append(command)
                            else:
                                raise Exception("Why are you using %s as an sbatch command?" % command.__class__.__name__)
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
                        cmdstring += "#SBATCH %s\n" % optionalargre.sub("",pdef.pattern)
                    else:
                        # Remove the question marks and substitute the VALUE
                        cmdstring += "#SBATCH %s\n" % pdef.pattern.replace("?","").replace("<VALUE>",value)
                        
                else:
                    if value == True:
                        cmdstring += "#SBATCH %s\n" % pdef.pattern
                    else:
                        cmdstring += "#SBATCH %s\n" % pdef.pattern.replace("<VALUE>",value)
                   
        cmdstring += "\n".join(commands)
        scriptfile = None                         
        if scriptname is None:
            # Generate a tempfile scriptname
            scriptfile = tempfile.NamedTemporaryFile(mode='w',suffix='.sbatch', dir=self.scriptpath,delete=False)
            scriptname = scriptfile.name
        else:
            if scriptname.startswith("/"):
                scriptfile = open(scriptname,'w')
            else:
                scriptname = os.path.join([self.scriptpath,scriptname])
                scriptfile = open(scriptname,'w')
        scriptfile.write(cmdstring)
        scriptfile.close()
               
        newcmdstring = ' '.join([self.bin,scriptname])
        return newcmdstring.encode('ascii','ignore')
    
