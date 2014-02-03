#!/usr/bin/env python

from distutils.core import setup

setup(name='webracer',
    version='0.2.0',
    description='Comprehensive web application testing library',
    author='Oleg Pudeyev',
    author_email='oleg@bsdpower.com',
    url='http://github.com/p/webracer',
    packages=['webracer', 'webracer.utils'],
    data_files=['LICENSE', 'README.rst'],
)
