"""
Created on Oct 9, 2014
Copyright (c) 2014
Harvard FAS Research Computing
All rights reserved.

@author: aaronkitzmiller
"""
import sys,os,time
import unittest
from command import Command
from command.slurm import SlurmRunner, ShellRunner

class Test(unittest.TestCase):


    def setUp(self):
        for f in ["howdy.err","howdy.out","howdy.sbatch","howdydoody.out","howdydoody.err","howdydoody.sbatch"]:
            try:
                os.remove(f)
            except Exception:
                pass
        self.confpath = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),'conf','14.03.8')

    def tearDown(self):
        pass
    
    def testArrayOfCommands(self):
        """
        Pass and array of Command objects to an sbatch and get a script with multiple 
        command lines
        """
        
        slurm = SlurmRunner(verbose=1)
        
        sbatch = Command.fetch('sbatch',path=self.confpath)
        
        sbatch.command = [Command("echo 'Howdy'"), Command("sleep 20"), Command("echo 'Doody'")]
        sbatch.partition = "serial_requeue"
        sbatch.mem = "100"
        sbatch.time = "5"
        sbatch.output = "howdydoody.out"
        sbatch.error = "howdydoody.err"
        sbatch.scriptname = "howdydoody.sbatch"
        sbatch.name = "howdydoodyjob"
        #print "Composed string is %s " % sbatch.composeCmdString()
        h = slurm.run(sbatch)
        self.assertTrue("Howdy\nDoody" in h.stdoutstr,"Stdout is '%s'" % h.stdoutstr)
        
        sbatch.command = ["echo 'Doody'","echo 'Howdy'"]
        h = slurm.run(sbatch)
        self.assertTrue("Doody\nHowdy" in h.stdoutstr,"Stdout is '%s'" % h.stdoutstr)


    def testSlurm(self):
        # Fetch command via parameter defs
        
        sbatch = Command.fetch('sbatch',path=self.confpath)
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
        slurm = SlurmRunner(verbose=1)
        h = slurm.run(sbatch)
        self.assertTrue("Usage: sbatch" in h.stdoutstr,h.stderrstr)
        
        # Do a simple echo in sbatch
        sbatch.usage = False
        sbatch.command = Command("sleep 20 && echo 'Howdy'")
        sbatch.partition = "serial_requeue"
        sbatch.mem = "100"
        sbatch.time = "5"
        sbatch.output = "howdy.out"
        sbatch.error = "howdy.err"
        sbatch.scriptname = "howdy.sbatch"
        sbatch.name = "howdyjob"
        #print "Composed string is %s " % sbatch.composeCmdString()
        h = slurm.run(sbatch)
        self.assertTrue(isinstance(sbatch.command,Command), 'sbatch.command should be a Command object')
        
        # Run squeue in a loop to get status information
        squeue = Command.fetch('squeue',path=self.confpath)
        squeue.jobs = h.jobid
        squeue.noheader = True
        sh = ShellRunner(verbose=1)        
        
        time.sleep(5)
        h2 = sh.run(squeue)
        while h2.stdoutstr:
            self.assertTrue(h.jobid in h2.stdoutstr,"out: %s\nerr: %s" % (h2.stdoutstr,h2.stderrstr))
            time.sleep(10)
            h2 = sh.run(squeue)
   
        self.assertTrue("Howdy" in h.stdoutstr)
        self.assertTrue(h.stderrstr == "")
        self.assertTrue(h.exitstatus == "COMPLETED")
        
        #Get sacct information
        sacct = Command.fetch('sacct',path=self.confpath)
        sacct.jobs = h.jobid
        sacct.format = "JobID,elapsed"
        sacct.noheader = True
        sacct.parsable = True
        h3 = sh.run(sacct)
        
        self.assertTrue(h.jobid in h3.stdoutstr,h3.stdoutstr)
        self.assertTrue("%s.batch" % h.jobid in h3.stdoutstr, h3.stdoutstr)
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
