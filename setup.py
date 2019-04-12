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
      packages=['examon', 'examon.plugin', 'examon.utils'],      
      install_requires=[
          'requests'
      ],
      zip_safe=False)
