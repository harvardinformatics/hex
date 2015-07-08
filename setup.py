"""
Created on April 30, 2015
Copyright (c) 2015
Harvard FAS Research Computing
All rights reserved.

@author: Aaron Kitzmiller
"""
import os
from setuptools import setup, find_packages

setup(
    name = "hex",
    version = "0.5",
    author='Aaron Kitzmiller <aaron_kitzmiller@harvard.edu>',
    author_email='aaron_kitzmiller@harvard.edu',
    description='Python modules for long running commands',
    license='LICENSE',
    keywords = "bioinformatics",
    url='http://pypi.python.org/pypi/hex/',
    packages = find_packages(),
    long_description=open('README.txt').read(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
    ],
)
