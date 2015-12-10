#!/usr/bin/env python3

from distutils.core import setup
from os.path import dirname, join

with open(join(dirname(__file__), 'README.rst')) as readme_file:
    long_description = '\n' + readme_file.read()

setup(name='infseq',
      description='Lazy infinite cached sequences',
      long_description=long_description,
      author='Dmitry Shachnev',
      author_email='mitya57@gmail.com',
      version='0.1',
      url='https://github.com/mitya57/infseq',
      py_modules=['infseq'],
      license='BSD')
