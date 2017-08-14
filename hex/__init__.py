"""
@date    : 2017-06-20 13:11:20
@author  : Aaron Kitzmiller (aaron_kitzmiller@harvard.edu)
@cersion : $Id$
@copyright : 2017 The Presidents and Fellows of Harvard College. All rights reserved.
"""
import logging
from config import Config

__version__ = "0.0.1"
DEFAULT_PDEF_PATH = "./config"
logging.basicConfig()
config = Config()


def getClassFromName(classname):
    """
    Utility that will return the class object for a full qualified
    classname
    """
    try:
        parts = classname.split(".")
        module = ".".join(parts[:-1])
        m = __import__(module)
        for comp in parts[1:]:
            m = getattr(m, comp)
        return m
    except ImportError:
        return None


class UserException(Exception):
    """
    Exceptions for known user errors
    """

    def __init__(self,message):
        super(UserException,self).__init__(message)
        self.user_msg = message


# __all__ = []

# import pkgutil
# import inspect

# for loader, name, is_pkg in pkgutil.walk_packages(__path__):
#     module = loader.find_module(name).load_module(name)

#     for name, value in inspect.getmembers(module):
#         if name.startswith("__"):
#             continue

#         globals()[name] = value
#         __all__.append(name)
