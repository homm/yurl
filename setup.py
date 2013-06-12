#!/usr/bin/env python

import sys
from setuptools import setup

tests_require = []
if sys.version_info < (2, 7):
    tests_require.append('unittest2')

setup(name='YURL',
      version='0.11',
      description='Yurl is alternative url manipulation library',
      long_description=open('README.rst', 'r').read(),
      author='Aleksadr Karpinsky',
      author_email='homm86@gmail.com',
      url='http://github.com/homm/yurl/',
      packages=['yurl'],
      tests_require=tests_require,
      test_suite='test')
