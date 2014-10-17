"""
Created on Oct 7, 2014
Copyright (c) 2014
Harvard FAS Research Computing
All rights reserved.

@author: Aaron Kitzmiller
"""
import os

class StringValidator(object):
    """
    Returns None if value is a valid parameter value string.  
    """
    def isValid(self,value):
        return None;


class PathValidator(StringValidator):
    """
    Returns None if the value is a valid path
    """
    def isValid(self,value):
        if os.path.exists(value):
            return None
        else:
            return "Path %s does not exist." 