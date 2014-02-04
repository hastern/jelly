#!/usr/bin/env python

import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

    
Name = "jelly"
Version = "1.0"
Description = 'wxPython based application framework',
Author = "Hanno Sternberg"
Mail = "hanno@almostintelligent.de"
Url = 'https://github.com/drakehutner/jelly'
Company = ''
Copyright = ''
   
setup(
	name=Name, version=Version, description=Description,
	author=Author, author_email=Mail, url=Url,
	py_modules=['view', 'logger', 'baseobjs', 'event','structure','shortcut','menu','plugin','gui','__init__'],
	license=read('LICENSE'),
	long_description=read('README.md'),
	install_requires=['pyparsing'],
	options = {},
	data_files=[],
	zipfile=None,
	zip_safe=True,
)
