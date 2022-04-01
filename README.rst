=========
eradicate
=========

.. image:: https://github.com/myint/eradicate/actions/workflows/test.yml/badge.svg
    :target: https://github.com/myint/eradicate/actions/workflows/test.yml
    :alt: Build status

----

``eradicate`` removes commented-out code from Python files.


Introduction
============

With modern revision control available, there is no reason to save
commented-out code to your repository. ``eradicate`` helps cleans up
existing junk comments. It does this by detecting block comments that
contain valid Python syntax that are likely to be commented out code.
(It avoids false positives like the sentence ``this is not good``,
which is valid Python syntax, but is probably not code.)


Example
=======

.. code-block:: bash

    $ eradicate --in-place example.py

Before running ``eradicate``.

.. code-block:: python

    #import os
    # from foo import junk
    #a = 3
    a = 4
    #foo(1, 2, 3)

    def foo(x, y, z):
        # print('hello')
        print(x, y, z)

        # This is a real comment.
        #return True
        return False

After running ``eradicate``.

.. code-block:: python

    a = 4

    def foo(x, y, z):
        print(x, y, z)

        # This is a real comment.
        return False


Whitelisting
============

False positives can happen so there is a whitelist feature to fix them shorthand.
You can either add entries to the default whitelist with ``--whitelist-extend`` or overwrite the default with ``--whitelist``.
Both arguments expect a string of ``#`` separated regex strings (whitespaces are preserved). E.g. ``eradicate --whitelist "foo#b a r" filename``
Those regex strings are matched case insensitive against the start of the comment itself.

For the default whitelist please see ``eradicate.py``.


Related
=======

There are different tools, plugins, and integrations for ``eradicate`` users:

- `flake8-eradicate <https://github.com/sobolevn/flake8-eradicate>`_ - Flake8 plugin to find commented out or dead code.
