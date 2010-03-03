from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='dctools',
      version=version,
      description="DC++ Tools",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='dc++',
      author='John-John Tedro',
      author_email='johnjohn.tedro@gmail.com',
      url='http://github.com/udoprog/dctools',
      license='GPLv3',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points={
        'console_scripts': [
          'dci = dctools:entrypoint',
        ],
      })
