#!/usr/bin/env python
#from distutils.core import setup

from setuptools import setup, find_packages

setup(name="metacram",
      version="0.5",
      description="Comparative Rapid Annotation of Metagenomes",
      license="GPLv3",
      author="Austin G. Davis-Richardson",
      author_email="harekrishna@gmail.com",
      url="http://github.com/audy/cramp",
      packages = find_packages(),
      keywords= "bioinformatics metagenome metagenomics",
      zip_safe = False,
      entry_points = { 
        'console_scripts':
        ['metacram = metacram.cram_cli:main']
      }
      )