"""
Created on Jan 7, 2015
Copyright (c) 2014
Harvard FAS Research Computing
All rights reserved.

@author: Aaron Kitzmiller
"""

import re
import logging

logger = logging.getLogger('slyme')

DEFAULT_SLURM_CONF_FILE="/etc/slurm/slurm.conf"

class Slurm(object):
    """
    Encapsulation of Slurmy things
    """
    def __init__(self,conffile=DEFAULT_SLURM_CONF_FILE):
        self.loadConfig(conffile)
        self.scancel = Command.fetch("scancel.json")
        self.sbatch  = Command.fetch("sbatch.json")
        self.sacct   = Command.fetch("sacct.json")
    
    def loadConfig(self,conffile):
        '''
        Constructs the object using the given slurm.conf file name
        
        If there are backslashes at the end of the line it's concatenated
        to the next one.
        
        NodeName lines are not saved because of the stupid DEFAULT stuff.  
        Maybe someday.
        '''
        logger.debug("Initializing SlurmConfig using %s" % conffile)
        currline = ''
        m = re.compile(r'([^=]+)\s*=\s*(.*)') #Used to extract name=value 
        n = re.compile(r'(\S+)\s+(.*)')       #Parse values on PartitionName
        with open(conffile,'rt') as f:
            for line in f:
                line = line.rstrip().lstrip()
                if line.startswith('#') or line.isspace() or not line:
                    continue
            
                # Concatenate lines with escaped line ending
                if line.endswith('\\'):
                    logger.debug("Concatenating line %s" % line)
                    currline += line.rstrip('\\')
                    continue
                
                currline += line
                
                # Skip nodename lines
                if currline.startswith('NodeName'):
                    currline = ''
                    continue
                
                # Split on first equal
                result = m.match(currline)
                if result is not None:
                    name = result.group(1)
                    value = result.group(2)
                    
                    # For PartitionName lines, we need to extract the name 
                    # and add it to the Partitions list
                    if name == 'PartitionName':
                        result2 = n.match(value)
                        if result2 is None:
                            logger.info("Bad PartitionName value %s.  Skipping." \
                                % value)
                            continue
                        pname = result2.group(1)
                        pvalue = result2.group(2)
                        if 'Partitions' not in self:
                            self['Partitions'] = {}
                        self['Partitions'][pname] = pvalue
                    else:                            
                        self[name] = value
                else:
                    logger.error("Slurm config file %s has strange line '%s'" % (conffile,currline))
                
                currline = ''
    
    def killJob(self,jobid=None):
        pass
    
    def getJobStatus(self,jobid=None):
        pass
    
    def submitJob(self,command,**kwargs):
        pass