#!/usr/bin/env python

from distutils.core import setup
import os.path

PACKAGE = "webracer"

setup(name=PACKAGE,
    version='0.2.0',
    description='Comprehensive web application testing library',
    author='Oleg Pudeyev',
    author_email='oleg@bsdpower.com',
    url='http://github.com/p/webracer',
    packages=['webracer', 'webracer.utils'],
    data_files=[(os.path.join('share', 'doc', PACKAGE), ('LICENSE', 'README.rst'))],
)
