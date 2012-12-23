=========
eradicate
=========

.. image:: https://travis-ci.org/myint/eradicate.png?branch=master
   :target: https://travis-ci.org/myint/eradicate
   :alt: Build status

Remove commented out code from Python files.

With modern revision control available there is no reason to save junk
comments to the repository. *eradicate* helps cleans things up existing junk.

-------
Example
-------

::

    $ eradicate --in-place example.py

Before::

   #a = 3
   a = 4
   #foo(1, 2, 3)

   def foo(x, y, z):
       #print('hello')
       print(x, y, z)

after::

   a = 4

   def foo(x, y, z):
       print(x, y, z)
