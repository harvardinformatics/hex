"""
Created on July 1, 2015
Copyright (c) 2015
Harvard FAS Research Computing
All rights reserved.

@author: Aaron Kitzmiller
"""
import os
from setuptools import setup, find_packages

setup(
    name = "hex",
    version = "0.1.0",
    author='Aaron Kitzmiller <aaron_kitzmiller@harvard.edu>',
    author_email='aaron_kitzmiller@harvard.edu',
    description='General command line wrapper classes that support parameters as attributes as well as persistent background processes',
    license='LICENSE.txt',
    keywords = "executables",
    url='http://pypi.python.org/pypi/hex/',
    packages = find_packages(),
    long_description=open('README.txt').read(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
    ],
)
