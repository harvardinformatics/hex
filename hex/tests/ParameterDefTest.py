"""
Created on Oct 6, 2014
Copyright (c) 2014
Harvard FAS Research Computing
All rights reserved.

@author: aaronkitzmiller
"""

import unittest
import os, sys, time
from command import Command,ShellRunner


class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testFetch(self):
        # Fetch command via parameter defs
        # confpath = os.path.join('../../','conf')
        argtest = Command.fetch('argtest',path=os.path.dirname(os.path.abspath(__file__)))
        self.assertTrue(argtest.bin == 'argtest.py')
        argtest.option = "option-value"
        argtest.quoted_option = 'Some stuff that has spaces and "a quoted" section'
        argtest.argument = "argument"
        argtest.optional_option = True
        argtest.boolean_option = True
        cmdstring = argtest.composeCmdString()
        self.assertTrue(cmdstring == 'argtest.py --boolean-option --optional-option --option=option-value --quoted-option="Some stuff that has spaces and \\"a quoted\\" section" "argument"',cmdstring)
        sh = ShellRunner()
        os.environ["PATH"] = ':'.join(["./",os.environ["PATH"]])
        h = sh.run(argtest)
        self.assertTrue("Boolean option set" in h.stdoutstr,h.stdoutstr)
        self.assertTrue("Optional option set" in h.stdoutstr,h.stdoutstr)
        self.assertTrue("Option set to option-value" in h.stdoutstr,h.stdoutstr)
        self.assertTrue("Quoted option set to Some stuff that has spaces and \"a quoted\" section" in h.stdoutstr,h.stdoutstr)
        self.assertTrue("Arg set to argument" in h.stdoutstr,h.stdoutstr)
        print h.stderrstr
        
        # Use "False" to turn off optional-option and boolean-option
        argtest.optional_option = False
        argtest.boolean_option = False
        cmdstring = argtest.composeCmdString()
        self.assertTrue('argtest.py --option=option-value --quoted-option="Some stuff that has spaces and \\"a quoted\\" section" "argument"' == cmdstring,cmdstring)
        h = sh.run(argtest)
        self.assertTrue("Boolean option set" not in h.stdoutstr,h.stdoutstr)
        self.assertTrue("Optional option set" not in h.stdoutstr,h.stdoutstr)
        self.assertTrue("Option set to option-value" in h.stdoutstr,h.stdoutstr)
        self.assertTrue("Quoted option set to Some stuff that has spaces and \"a quoted\" section" in h.stdoutstr,h.stdoutstr)
        self.assertTrue("Arg set to argument" in h.stdoutstr,h.stdoutstr)
        
        # Optional option with a value
        argtest.optional_option = "optional-option"
        cmdstring = argtest.composeCmdString()
        self.assertTrue('argtest.py --optional-option=optional-option --option=option-value --quoted-option="Some stuff that has spaces and \\"a quoted\\" section" "argument"' == cmdstring,cmdstring)
        h = sh.run(argtest)
        self.assertTrue("Boolean option set" not in h.stdoutstr,h.stdoutstr)
        self.assertTrue("Optional option value optional-option" in h.stdoutstr,h.stdoutstr)
        self.assertTrue("Option set to option-value" in h.stdoutstr,h.stdoutstr)
        self.assertTrue("Quoted option set to Some stuff that has spaces and \"a quoted\" section" in h.stdoutstr,h.stdoutstr)
        self.assertTrue("Arg set to argument" in h.stdoutstr,h.stdoutstr)
        
        # Bad parameter does not get added to command line 
        argtest.junk = "junk"
        cmdstring = argtest.composeCmdString()
        self.assertTrue('argtest.py --optional-option=optional-option --option=option-value --quoted-option="Some stuff that has spaces and \\"a quoted\\" section" "argument"' == cmdstring,cmdstring)
        h = sh.run(argtest)
        self.assertTrue("Boolean option set" not in h.stdoutstr,h.stdoutstr)
        self.assertTrue("Optional option value optional-option" in h.stdoutstr,h.stdoutstr)
        self.assertTrue("Option set to option-value" in h.stdoutstr,h.stdoutstr)
        self.assertTrue("Quoted option set to Some stuff that has spaces and \"a quoted\" section" in h.stdoutstr,h.stdoutstr)
        self.assertTrue("Arg set to argument" in h.stdoutstr,h.stdoutstr)
       
        
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testFetch']
    unittest.main()