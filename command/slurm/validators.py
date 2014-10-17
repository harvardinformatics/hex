"""
Created on Oct 7, 2014
Copyright (c) 2014
Harvard FAS Research Computing
All rights reserved.

@author: Aaron Kitzmiller
"""

class BeginTimeValidator(object):
    """
    Validates the --begin parameter for sbatch
    """
    def isValid(self,value):
        return None;