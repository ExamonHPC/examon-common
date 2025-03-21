# -*- coding: utf-8 -*-
from setuptools import setup

setup(name='examon-common',
      version='v0.2.6',
      description='Examon common utilities',
      url='http://github.com/fbeneventi/examon-common',
      author='Francesco Beneventi',
      author_email='beneventi.francesco@gmail.com',
      license='MIT',
      packages=['examon', 'examon.plugin', 'examon.utils', 'examon.db', 'examon.transport'],      
      install_requires=[
          'requests == 2.32.3',
          'paho-mqtt == 1.6.1',
          'setuptools == 66.1.1',
          'concurrent-log-handler == 0.9.25',
          'pytest == 8.3.4',
          'pytest-mock == 3.14.0',
          'psutil == 6.1.1'
      ],
      zip_safe=False)

