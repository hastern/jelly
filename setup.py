#!/usr/bin/env python

import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
	name             = "jelly", 
	version          = "1.1.1", 
	description      = 'wxPython based application framework',
	author           = "Hanno Sternberg",
	author_email     = "hanno@almostintelligent.de", 
	url              = 'https://github.com/drakehutner/jelly',
	py_modules       = ['__init__', 'logger', 'plugin', 'event', 'gui', 'view', 'menu', 'baseobjs', 'structure', 'shortcut'],
	license          = read('LICENSE'),
	long_description = read('README.md'),
#	install_requires = ['wxpython'],
	options          = {},
	data_files       = [],
	test_suite       = "jelly_test",
	zipfile          = None,
	zip_safe         = True,
)
