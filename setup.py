__author__ = 'samantha'
from setuptools import setup, find_packages
packages = find_packages(exclude=['test'])

setup(name='sqluop',
      version='0.1',
      description='type information for uop ',
      author='Samantha Atkins',
      author_email='sjatkins@protonmail.com',
      license='internal',
      packages=packages,
      install_requires = ['uop', 'pytest', 'sjautils', 'sqlalchemy'],
      zip_safe=False)
