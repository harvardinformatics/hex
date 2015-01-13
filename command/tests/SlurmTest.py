"""
Created on Oct 9, 2014
Copyright (c) 2014
Harvard FAS Research Computing
All rights reserved.

@author: aaronkitzmiller
"""
import sys,os
import unittest
from command import Command
from command.slurm import SlurmRunner

class Test(unittest.TestCase):


    def setUp(self):
        for f in ["howdy.err","howdy.out","howdy.sbatch"]:
            try:
                os.remove(f)
            except Exception:
                pass


    def tearDown(self):
        pass


    def testSlurm(self):
        # Fetch command via parameter defs
        confpath = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),'conf')
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
        sh = SlurmRunner(verbose=1)
        h = sh.run(sbatch)
        self.assertTrue("Usage: sbatch" in h.stdoutstr,h.stderrstr)
        
        # Do a simple echo
        sbatch.usage = False
        sbatch.command = "echo 'Howdy'"
        sbatch.partition = "serial_requeue"
        sbatch.mem = "100"
        sbatch.time = "5"
        sbatch.output = "howdy.out"
        sbatch.error = "howdy.err"
        sbatch.scriptname = "howdy.sbatch"
        print "Composed string is %s " % sbatch.composeCmdString()
        h = sh.run(sbatch)
        self.assertTrue("Howdy" in h.stdoutstr)
        self.assertTrue(h.stderrstr == "")
        self.assertTrue(h.exitstatus == "COMPLETED")


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
