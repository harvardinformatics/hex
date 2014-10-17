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
DEFAULT_PDEF_PATH='../conf'


def getClassFromName(classname):
    """
    Utility that will return the class object for a full qualified 
    classname
    """
    parts = classname.split('.')
    module = ".".join(parts[:-1])
    m = __import__( module )
    for comp in parts[1:]:
        m = getattr(m, comp)            
    return m


__all__ = []

import pkgutil
import inspect

for loader, name, is_pkg in pkgutil.walk_packages(__path__):
    module = loader.find_module(name).load_module(name)

    for name, value in inspect.getmembers(module):
        if name.startswith('__'):
            continue

        globals()[name] = value
        __all__.append(name)
        
        

            
