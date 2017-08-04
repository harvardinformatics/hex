from .bashsystem import *
from hex import UserException,getClassFromName


def getSystem(systemkey="bash", runlogger = None):
    """
    Return the system by key.  If no key is given, bash is returned
    """
    availablesystems = getAvailableSystems()
    if systemkey not in availablesystems.keys():
        raise UserException("System %s is not available.  Available systems include %s" % (systemkey,availablesystems.keys()))
    classname = availablesystems[systemkey]
    systemcls = getClassFromName(classname)
    return systemcls(runlogger = runlogger)


def getAvailableSystems():
    """
    Return a hash of the available system classes, keyed by short name.
    """

    return {
        "bash" : "hex.system.bashsystem.BashSystem",
    }
