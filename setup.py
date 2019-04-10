# -*- coding: utf-8 -*-
from setuptools import setup

setup(name='examon-common',
      version='0.0.1',
      description='Examon common utilities',
      url='http://github.com/fbeneventi/examon-common',
      author='Francesco Beneventi',
      author_email='francesco.beneventi@unibo.it',
      license='MIT',
      packages=['examon', 'examon.plugin', 'examon.utils'],      
      install_requires=[
          'requests'
      ],
      zip_safe=False)
