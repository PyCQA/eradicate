=========
eradicate
=========

.. image:: https://travis-ci.org/myint/eradicate.png?branch=master
    :target: https://travis-ci.org/myint/eradicate
    :alt: Build status

.. image:: https://coveralls.io/repos/myint/eradicate/badge.png?branch=master
    :target: https://coveralls.io/r/myint/eradicate
    :alt: Test coverage status

*eradicate* removes commented-out code from Python files.


Introduction
============

With modern revision control available, there is no reason to save
commented-out code to your repository. *eradicate* helps cleans up
existing junk comments. It does this by detecting block comments that
contain valid Python syntax that are likely to be commented out code.
(It avoids false positives like the sentence ``this is not good``,
which is valid Python syntax, but is probably not code.)


Example
=======

::

    $ eradicate --in-place example.py

Before running eradicate.

.. code-block:: python

    #import os
    #from foo import junk
    #a = 3
    a = 4
    #foo(1, 2, 3)

    def foo(x, y, z):
        #print('hello')
        print(x, y, z)

        # This is a real comment.
        #return True
        return False

After running eradicate.

.. code-block:: python

    a = 4

    def foo(x, y, z):
        print(x, y, z)

        # This is a real comment.
        return False
