"""
Created on Sep 29, 2014
Copyright (c) 2014
Harvard FAS Research Computing
All rights reserved.

@author: Aaron Kitzmiller
"""

import unittest
import os, sys, time
from stat import S_IXUSR, S_IWUSR, S_IRUSR
from cmd import RunLog, ShellRunner, DefaultFileLogger, Command

import datetime

class Test(unittest.TestCase):
        
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def testRunLogger(self):
        
        # Create a RunSet and save it
        runset = []
        runset.append(RunLog(   jobid='1234',
                                hostname='localhost',
                                cmdstring="echo 'Hello'",
                                starttime=datetime.datetime.now())
                      )
        logger = DefaultFileLogger()
        runsetfilename = logger.saveRunSet(runset, 'testrunset')
        runsettext = open(runsetfilename,'r').readlines()
        
        # Check file text contents
        self.assertTrue("jobid: '1234'" in runsettext[0],runsettext)
        self.assertTrue("cmdstring: echo 'Hello'" in runsettext[0],runsettext)
        self.assertTrue("hostname: localhost" in runsettext[0],runsettext)
        self.assertTrue("starttime: '2014-" in runsettext[0],runsettext)
        
        # Retrieve as RunSet
        runset = logger.getRunSet('testrunset')
        self.assertTrue(runset[0]['jobid'] == '1234')
        self.assertTrue(runset[0]['cmdstring'] == "echo 'Hello'")
        self.assertTrue(runset[0]['hostname'] == "localhost")
        
        # Update existing RunSet
        runset[0]['endtime'] = datetime.datetime.now()
        logger.saveRunSet(runset,'testrunset')
        
        runset2 = logger.getRunSet('testrunset')
        self.assertTrue(runset2[0]['jobid'] == '1234')
        self.assertTrue(runset2[0]['endtime'].year == datetime.datetime.now().year)
        self.assertTrue(runset2[0]['endtime'].month == datetime.datetime.now().month)
        self.assertTrue(runset2[0]['endtime'].day == datetime.datetime.now().day)

        # Missing required field
        self.assertRaises(Exception, lambda: RunLog(jobid='1234', hostname='localhost',cmdstring="echo 'Hello'"))
                               
        
    def testCommand(self):
        
        # Verify proper command string construction
        print "Testing simple commands"
        cmd = Command("echo 'Hello'")
        self.assertTrue(cmd.composeCmdString() == "echo 'Hello'")
        cmd = Command("echo","'Hello'")
        self.assertTrue(cmd.composeCmdString() == "echo 'Hello'")
        cmd = Command("echo","-n","'Hello'")
        self.assertTrue(cmd.composeCmdString() == "echo -n 'Hello'")
        cmd = Command("echo","'Hello'",n=True)
        self.assertTrue(cmd.composeCmdString() == "echo 'Hello' -n", cmd.composeCmdString())
        cmd = Command("test",arg1="value1",arg2="value2",arg3="value3")
        self.assertTrue(cmd.composeCmdString() == "test --arg1=value1 --arg2=value2 --arg3=value3",cmd.composeCmdString())
        
    
    def testShellRunner(self):
         
        ## Direct string execution, stdout string
        print "Test echo"
        r = ShellRunner()
        h = r.run("echo 'Hello'")
        self.assertEqual(h.stdoutstr, "Hello\n")
        self.assertEqual(h.stderrstr,"")
        print "Done"
         
        ## Direct string execution, stderr string
        print "Test error result"
        h = r.run("cat nosuchfile")
        self.assertEqual(h.stdoutstr,"")
        self.assertEqual(h.stderrstr,"cat: nosuchfile: No such file or directory\n")
        print "Done"
        
        ## Run a long binary that prints to both stderr and stdout
        script = '''
#!/bin/bash

n="0"

while [[ $n -lt 40 ]]
do
  echo "All work and no play makes Jack a dull boy" >/dev/stderr
  echo "All work and no play makes Jane a dull girl" >/dev/stdout
  sleep 2 
  n=$[$n + 1]

done
        '''.strip()
        
        with open("long.sh","w") as scriptfile:
            scriptfile.write(script)
            
        os.chmod("long.sh", S_IXUSR | S_IRUSR | S_IWUSR)
        print "Running long.sh..."
        h = r.run("bash long.sh")
        stdoutstr = h.stdoutstr
        stderrstr = h.stderrstr
        print "Done."
          
        self.assertEqual(len(stdoutstr.split("\n")), 41, len(stdoutstr.split("\n")))
        self.assertEqual(len(stderrstr.split("\n")), 41, len(stderrstr.split("\n")))
          
        ## Direct string execution, stdout iterator
        print "Starting long.sh..."
        h = r.run("bash long.sh")
        stdout = h.stdout
        lines = []
        while h.checkStatus() is None:
            where = stdout.tell()
            line = stdout.readline()
            if not line:
                time.sleep(1)
                stdout.seek(where)
            else:
                lines.append(line.strip())
                  
        self.assertEquals(len(lines), 40, lines)
        self.assertTrue('Jane a dull girl' in lines[0], lines[0])
                  
        ## Direct string execution, stderr iterator
        print "Starting long.sh..."
        h = r.run("bash long.sh")
        stderr = h.stderr
        lines = []
        while h.checkStatus() is None:
            where = stderr.tell()
            line = stderr.readline()
            if not line:
                time.sleep(1)
                stderr.seek(where)
            else:
                lines.append(line.strip())
                  
        self.assertEquals(len(lines), 40, lines)
        self.assertTrue('Jack a dull boy' in lines[0], lines[0])
        
        ## Fail before ending and return non-zero
        script = '''
#!/bin/bash

n="0"

while [[ $n -lt 10 ]]
do
  echo "All work and no play makes Jane a dull girl" >/dev/stdout
  sleep 2 
  n=$[$n + 1]
done
echo "Fail!" >/dev/stderr
exit 2
        '''.strip()
        
        with open("fail.sh","w") as scriptfile:
            scriptfile.write(script)
            
        os.chmod("fail.sh", S_IXUSR | S_IRUSR | S_IWUSR)
        print "Running fail.sh..."
        h = r.run("bash fail.sh")
        exitcode = h.exitcode
        stdoutstr = h.stdoutstr
        stderrstr = h.stderrstr
        self.assertTrue(len(stdoutstr.split("\n")) == 11,len(stdoutstr.split("\n")))
        self.assertTrue('Fail!' in stderrstr,stderrstr)
        self.assertTrue(exitcode == 2,exitcode)
        
        
    def testRcx(self):
        """
        Test the rcx.py tool that launches a job.  Then connect to the 
        stderr / stdout stream of that job using the runset information
        """
        
    
