=========
eradicate
=========

.. image:: https://travis-ci.org/myint/eradicate.png?branch=master
   :target: https://travis-ci.org/myint/eradicate
   :alt: Build status

*eradicate* removes commented-out code from Python files.

------------
Introduction
------------

With modern revision control available there is no reason to save junk
comments to your repository. *eradicate* helps cleans up existing junk.
It does this by first tokenizing the code to find the comments. It then
removes the block comments that both contain valid Python syntax and
have symbols unlikely to be real comment.

-------
Example
-------

::

    $ eradicate --in-place example.py

Before::

   #import os
   #from foo import junk
   #a = 3
   a = 4
   #foo(1, 2, 3)

   def foo(x, y, z):
       #print('hello')
       print(x, y, z)

After::

   a = 4

   def foo(x, y, z):
       print(x, y, z)
