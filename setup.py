#!/usr/bin/env python

import sys
import codecs
from setuptools import setup


setup(name='YURL',
      version='1.0.0',
      description='Yurl is alternative url manipulation library',
      long_description=codecs.open('README.rst', 'r', 'utf-8').read(),
      author='Aleksadr Karpinsky',
      author_email='homm86@gmail.com',
      url='http://github.com/homm/yurl/',
      packages=['yurl'],
      test_suite='test',
)
