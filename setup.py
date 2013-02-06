#!/usr/bin/env python
"""Setup for eradicate."""

import ast
from distutils import core


def version():
    """Return version string."""
    with open('eradicate.py') as input_file:
        for line in input_file:
            if line.startswith('__version__'):
                return ast.parse(line).body[0].value.s


with open('README.rst') as readme:
    core.setup(name='eradicate',
               version=version(),
               description='Removes commented-out code.',
               long_description=readme.read(),
               license='Expat License',
               author='myint',
               url='https://github.com/myint/eradicate',
               classifiers=['Intended Audience :: Developers',
                            'Environment :: Console',
                            'Programming Language :: Python :: 2.7',
                            'Programming Language :: Python :: 3',
                            'License :: OSI Approved :: MIT License'],
               keywords='clean, format, commented-out code',
               py_modules=['eradicate'],
               scripts=['eradicate'])
