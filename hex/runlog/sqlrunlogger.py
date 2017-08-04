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
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker

class SQLRunLogger(DefaultRunLogger):

    """
    Saves RunLogs to sql db in addition to default behavior
    """
    def __init__(self):
        self.session = self.create_db()
        super(SQLRunLogger, self).__init__()

    def save(self, runlog):
        # save command to file with default
        ret = super(SQLRunLogger, self).save(runlog)
        # log to db
        runlog = Log(**runlog)
        self.session.add(runlog)
        self.session.commit()
        return ret

    def create_db(self):
        # sqllite in memory will not remember rows between runs
        # TODO: use mysql
        self.engine = create_engine('sqlite:///:memory:', echo=True)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        return Session()

Base = declarative_base()
class Log(Base):
    __tablename__ = 'log'

    id = Column(Integer, primary_key=True)
    status = Column(String)
    result = Column(String)
    cmd = Column(String)
    stderrfile = Column(String)
    hostname = Column(String)
    system = Column(String)
    jobid = Column(String)
    scriptfilepath = Column(String)
    runid = Column(String)
    starttime = Column(String)
    endtime = Column(String)
    interpreter = Column(String)
    stdoutfile = Column(String)


