#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Config

| Uses json to parse any existing config files with precedence given to
the last in this order: global, cluster_hex, lab_hex, my_hex

@date      : 2017-06-23 16:03:57
@author    : Meghan Porter-Mahoney (mportermahoney@g.harvard.edu)
@version   : $Id$
@copyright : 2017 The Presidents and Fellows of Harvard College. All rights reserved.
@license   : GPLv2

"""
import json
import os

class Config(object):

    """
    Saves RunLogs to sql db in addition to default behavior
    """

    DEFAULT_SECTION = 'DEFAULT'
    SECTIONS = {DEFAULT_SECTION: {}, 'DB': {}}
    CONFIG_LEVELS = ['my_hex', 'lab_hex', 'cluster_hex', 'global', 'secret']
    ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

    def __init__(self):
        self.params = self.SECTIONS
        # load configs from lowest to highest level overwritting with update
        for name in self.CONFIG_LEVELS:
            level = self.read_config(name)
            for section in self.params:
                if section in level:
                    self.params[section].update(level[section])

    def read_config(self, name):
        params = {}
        try:
            # TODO: consider path for custom levels, prob not root
            path = self.ROOT_PATH + '/' + name + '.json'
            with open(path) as data:
                params = json.load(data)
        except:
            pass
        return params

    def set_defaults(self, parameterdefs):
        for i, param in enumerate(parameterdefs):
            if param['name']:
                param_lw = param['name'].lower()
                # if config exists then set as default
                if param_lw in self.params[self.DEFAULT_SECTION]:
                    parameterdefs[i]['default'] = self.params[self.DEFAULT_SECTION][param_lw]
        return parameterdefs

    def get_config(self, section):
        return self.params[section]
