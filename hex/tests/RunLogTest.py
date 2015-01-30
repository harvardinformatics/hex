'''
Created on Jan 29, 2015

@author: akitzmiller
'''
import unittest
import subprocess, glob, os
import yaml
from hex import RunHandler, DefaultFileLogger


class Test(unittest.TestCase):
    """
    Make sure the RunLogs work as expected (record the correct elements of the
    execution, support retrieval of stdout, stderr from separate processes)
    """


    def setUp(self):
        filestoremove = glob.glob("*.yaml")
        filestoremove.extend(glob.glob("*.stderr"))
        filestoremove.extend(glob.glob("*.stdout"))
        for f in filestoremove:
            os.remove(f)


    def tearDown(self):
        pass


    def testRunLog(self):
        """
        Launch long.sh from a ShellRunner in long.py, then get the stdout /stderr
        from this process.  Demonstrates detachability.
        """
        logpath = "./"
        runsetname = "testlong"
        subprocess.call("./long.py --log-path=%s --runset-name=%s" % (logpath,runsetname),shell=True)
        
        runsetlogfile = "%s.yaml" % runsetname
        runsetdata = yaml.load(open(runsetlogfile,"r"))
        data = runsetdata[0]
        self.assertTrue(data["cmdstring"] == "./long.sh", "cmdstring is wrong %s" % data["cmdstring"])
        self.assertTrue(data["runner"] == "shellrunner.ShellRunner", "runner is wrong %s" % data["runner"])
        
        rh = RunHandler(DefaultFileLogger(logpath),runsetname)
        stdout = rh.getStdOutString()
        stderr = rh.getStdErrString()
        
        self.assertTrue("All work and no play makes Jane a dull girl" in stdout,"stdout is bad %s" % stdout)
        self.assertTrue("All work and no play makes Jack a dull boy" in stderr,"stderr is bad %s" % stderr)
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.tests']
    unittest.main()