"""
Created on July 1, 2015
Copyright (c) 2015
Harvard FAS Research Computing
All rights reserved.

@author: Aaron Kitzmiller
"""
import os
from setuptools import setup, find_packages

def getVersion():
    version = '0.0.0'
    with open('hex/__init__.py','r') as f:
        contents = f.read().strip()

    m = re.search(r"__version__ = '([\d\.]+)'", contents)
    if m:
        version = m.group(1)
    return version

setup(
    name = "hex",
    version = getVersion(),
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
    entry_points={
        'console_scripts': [
            'hex=hex.cli:main',
        ]
    },
)
