#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Config

| Uses ConfigParser to parse any existing config files with precedence given to
the last in this order: global, cluster, lab, individual

@date      : 2017-06-23 16:03:57
@author    : Meghan Porter-Mahoney (mportermahoney@g.harvard.edu)
@version   : $Id$
@copyright : 2017 The Presidents and Fellows of Harvard College. All rights reserved.
@license   : GPLv2

"""

from ConfigParser import SafeConfigParser, NoOptionError

class Config(object):

    """
    Saves RunLogs to sql db in addition to default behavior
    """
    def __init__(self):
        self.parser = SafeConfigParser()
        self.parser.read('global.ini')
        self.parser.read('secret.ini')
        # TODO: need to use full path
        self.parser.read('~/hex.ini')

    def set_defaults(self, parameterdefs):
        for i, param in enumerate(parameterdefs):
            if param['name']:
                try:
                    default = self.parser.get('DEFAULT', param['name'].lower())
                    parameterdefs[i]['default'] = default
                # ignore this error and just don't set a default if none exists
                except NoOptionError as e:
                    pass
        return parameterdefs

    def get_config(self, section):
        return dict(self.parser.items(section))
