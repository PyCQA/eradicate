#!/usr/bin/env python

"""Setup for eradicate."""

from __future__ import unicode_literals

import ast
from setuptools import setup


def version():
    """Return version string."""
    with open('eradicate.py') as input_file:
        for line in input_file:
            if line.startswith('__version__'):
                return ast.parse(line).body[0].value.s


with open('README.rst') as readme:
    setup(
        name='eradicate',
        version=version(),
        description='Removes commented-out code.',
        long_description=readme.read(),
        license='Expat License',
        author='Steven Myint',
        url='https://github.com/myint/eradicate',
        classifiers=['Environment :: Console',
                     'Intended Audience :: Developers',
                     'License :: OSI Approved :: MIT License',
                     'Programming Language :: Python :: 2.7',
                     'Programming Language :: Python :: 3',
                     'Topic :: Software Development :: Quality Assurance'],
        keywords='clean, format, commented-out code',
        py_modules=['eradicate'],
        scripts=['eradicate'])
