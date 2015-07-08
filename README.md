# hex - Harvard Executables

hex is a python API for running shell commands used in Harvard FAS Informatics.
Though it will run a plain command string and return all three elements
(return code, stdout, and stderr) with a simpler interface than subprocess.Popen,
the library supports a couple of additional enhancements:

* Structured parameter definitions.
Using a JSON syntax, command parameters can be structured with explict names, switches,
and validation.  In addition to improving console use (parameters become object
attributes), command parameters can be validate prior to execution, or presented
intelligently in web or command line applications.

* Asynchronous execution
Using the ShellRunner class, commands can be run asynchronously and checked for
results at later time.  Command strings and their associated process id are stored
in a file that can be accessed later.  Status is easily checked and stdout / stderr
retrieved from this file


### run a simple command synchronously, returning the return code,
stdout and stderr

```python

>>> from hex import Command
>>> cmd = Command("hostname")
>>> [code,stdout,stderr] = cmd.run()
>>> print stdout
RC-AKITZMILLER-1.local
>>> print code
0
```


### Load parameter definitions from a string


### Load parameter definitions from a file


### Run a command with the ShellRunner and get the results back


### Run a command with the ShellRunner, close the console and get the back later.


