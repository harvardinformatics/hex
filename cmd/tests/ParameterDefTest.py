"""
Created on Oct 6, 2014
Copyright (c) 2014
Harvard FAS Research Computing
All rights reserved.

@author: aaronkitzmiller
"""

import unittest
import os, sys, time
from cmd import Command


class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testFetch(self):
        # Fetch command via parameter defs
        confpath = os.path.join('../../','conf')
        sbatch = Command.fetch('sbatch',path=confpath)
        self.assertTrue(sbatch.bin == 'sbatch')


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testFetch']
    unittest.main()