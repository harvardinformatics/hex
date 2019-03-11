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
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from hex import config

 class SQLRunLogger(DefaultRunLogger):

     """
     Saves RunLogs to sql db in addition to default behavior
     """
     def __init__(self, db = 'default'):
         super(SQLRunLogger, self).__init__()
         self.set_db(db)

    def set_db(self, db):
        db_params = config.get_config('DB')
        default = 'mysql://{user}:{password}@{server}/{database}'.format(**db_params)
        if db == 'default':
            self.db = default
        elif db == 'test': # use sqlite for testing
            self.db = 'sqlite:///:memory:'
        else:
            self.db = db

     def save(self, runlog):
         # save command to file with default
         ret = super(SQLRunLogger, self).save(runlog)
         # log to db
         try:
             self.session = self.create_db()
             runlog = SQLRunLog(**runlog)
             self.session.add(runlog)
             self.session.commit()
         except Exception as e:
             print('Error logging to db, default logging to file only: ' + str(e))
         return ret

     def create_db(self):
         # sqllite in memory will not remember rows between runs
         # TODO: use mysql
         self.engine = create_engine(self.db)
         Base.metadata.create_all(self.engine)
         Session = sessionmaker(bind=self.engine)
         return Session()

     def get_row(self, runid):
         row_dict = {}
         if runid:
             row = (self.session.query(SQLRunLog)
                     .filter_by(runid = runid).first())
             if row:
                 row_dict = row.__dict__
                 # remove non column, sqlalchemy object returns
                 row_dict.pop('_sa_instance_state', None)
         return row_dict

 Base = declarative_base()
 class SQLRunLog(Base):
     __tablename__ = 'runlog'

     id = Column(Integer, primary_key=True)
     status = Column(String(255))
     result = Column(String(255))
     cmd = Column(String(255))
     stderrfile = Column(String(255))
     hostname = Column(String(100))
     system = Column(String(100))
     jobid = Column(Integer)
     scriptfilepath = Column(String(255))
     runid = Column(String(100))
     starttime = Column(DateTime)
     endtime = Column(DateTime)
     interpreter = Column(String(100))
     stdoutfile = Column(String(255))


