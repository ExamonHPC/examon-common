# -*- coding: utf-8 -*-
from setuptools import setup

# version = {}
# with open('./examon/version.py') as fp:
    # exec(fp.read(), version)

setup(name='examon-common',
      use_scm_version={
               'local_scheme': 'dirty-tag',
               'write_to': 'examon/version.py'},
      setup_requires=['setuptools_scm'],
      description='Examon common utilities',
      url='http://github.com/fbeneventi/examon-common',
      author='Francesco Beneventi',
      author_email='francesco.beneventi@unibo.it',
      license='MIT',
      packages=['examon', 'examon.plugin', 'examon.utils', 'examon.db', 'examon.transport'],      
      install_requires=[
          'requests >= 2.21.0',
          'paho-mqtt >= 1.4.0',
          'futures >= 3.2.0',
          'setuptools >= 40.6.3',
          'concurrent-log-handler >= 0.9.16'
      ],
      zip_safe=False)
