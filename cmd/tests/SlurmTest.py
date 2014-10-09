"""
Created on Oct 9, 2014
Copyright (c) 2014
Harvard FAS Research Computing
All rights reserved.

@author: aaronkitzmiller
"""
import sys,os
import unittest
from cmd import Command,ShellRunner

class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testSlurm(self):
        # Fetch command via parameter defs
        confpath = os.path.join('../../','conf')
        sbatch = Command.fetch('sbatch',path=confpath)
        self.assertTrue(sbatch.__class__.__name__ == "SbatchCommand")
        self.assertTrue(sbatch.bin == 'sbatch')
        
        # Make sure the Command exposes parameters as attrs
        attrs = sbatch.__dir__()
        self.assertTrue("array" in attrs,attrs)
        self.assertTrue("exclude" in attrs,attrs)
        self.assertTrue("bin" in attrs,attrs)
        
        # Construct a test Command
        sbatch.usage = True
        print sbatch.composeCmdString()
        sh = ShellRunner(verbose=1)
        h = sh.run(sbatch)
        print h.stdoutstr
        print h.stderrstr


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()