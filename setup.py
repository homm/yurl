#!/usr/bin/env python

import sys
import codecs
from setuptools import setup


tests_require = []
if sys.version_info < (2, 7):
    tests_require.append('unittest2')

setup(name='YURL',
      version='0.13',
      description='Yurl is alternative url manipulation library',
      long_description=codecs.open('README.rst', 'r', 'utf-8').read(),
      author='Aleksadr Karpinsky',
      author_email='homm86@gmail.com',
      url='http://github.com/homm/yurl/',
      packages=['yurl'],
      tests_require=tests_require,
      test_suite='test')
