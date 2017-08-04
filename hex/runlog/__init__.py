from .runlog import *
from .defaultrunlogger import *
from .sqlrunlogger import *
from hex import UserException, getClassFromName

DEFAULT_RUN_LOGGER_NAME = 'default'

def getRunLogger(runlogger = None):
    """
    Return the runlogger class or default
    """
    available_run_loggers = getAvailableRunLoggers()
    if runlogger in available_run_loggers.keys():
        classname = available_run_loggers[runlogger]
    else:
        classname = available_run_loggers[DEFAULT_RUN_LOGGER_NAME]
    run_logger_class = getClassFromName(classname)
    return run_logger_class()

def getAvailableRunLoggers():
    """
    Return a hash of the available runlogger classes, keyed by short name.
    """

    return {
        "default" : "hex.runlog.defaultrunlogger.DefaultRunLogger",
        "sql" : "hex.runlog.sqlrunlogger.SQLRunLogger"
    }
