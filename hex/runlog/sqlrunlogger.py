#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SQL RunLogger

| Uses SQLAlchemy to read and write RunLogs to a database

@date      : 2017-06-23 16:03:57
@author    : Meghan Porter-Mahoney (mportermahoney@g.harvard.edu)
@version   : $Id$
@copyright : 2017 The Presidents and Fellows of Harvard College. All rights reserved.
@license   : GPLv2

"""

from hex.runlog.defaultrunlogger import DefaultRunLogger

class SQLRunLogger(DefaultRunLogger):

    """
    Saves RunLogs to sql db in addition to default behavior
    """
    def __init__(self):
        super(SQLRunLogger, self).__init__()
