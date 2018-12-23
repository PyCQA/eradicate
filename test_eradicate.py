#!/usr/bin/env python

"""Test suite for eradicate."""

from __future__ import unicode_literals

import contextlib
import io
import subprocess
import sys
import tempfile
import unittest

import eradicate


class UnitTests(unittest.TestCase):

    def test_comment_contains_code(self):
        self.assertFalse(eradicate.comment_contains_code(
            '#'))

        self.assertFalse(eradicate.comment_contains_code(
            '# This is a (real) comment.'))

        self.assertFalse(eradicate.comment_contains_code(
            '# 123'))

        self.assertFalse(eradicate.comment_contains_code(
            '# 123.1'))

        self.assertFalse(eradicate.comment_contains_code(
            '# 1, 2, 3'))

        self.assertFalse(eradicate.comment_contains_code(
            'x = 1  # x = 1'))

        self.assertFalse(eradicate.comment_contains_code(
            '# pylint: disable=redefined-outer-name'))

        self.assertFalse(eradicate.comment_contains_code(
            '# Issue #999: This is not code'))

        self.assertTrue(eradicate.comment_contains_code(
            '# x = 1'))

        self.assertTrue(eradicate.comment_contains_code(
            '#from foo import eradicate'))

        self.assertTrue(eradicate.comment_contains_code(
            '#import eradicate'))

        self.assertTrue(eradicate.comment_contains_code(
            '#"key": value,'))

        self.assertTrue(eradicate.comment_contains_code(
            '#"key": "value",'))

        self.assertTrue(eradicate.comment_contains_code(
            '#"key": 1 + 1,'))

        self.assertTrue(eradicate.comment_contains_code(
            "#'key': 1 + 1,"))

        self.assertTrue(eradicate.comment_contains_code(
            '#"key": {'))

        self.assertTrue(eradicate.comment_contains_code(
            '#}'))

        self.assertTrue(eradicate.comment_contains_code(
            '#} )]'))

        self.assertTrue(eradicate.comment_contains_code(
            '#},'))

    def test_comment_contains_code_with_print(self):
        self.assertTrue(eradicate.comment_contains_code(
            '#print'))

        self.assertTrue(eradicate.comment_contains_code(
            '#print(1)'))

        self.assertTrue(eradicate.comment_contains_code(
            '#print 1'))

        self.assertFalse(eradicate.comment_contains_code(
            '#to print'))

    def test_comment_contains_code_with_return(self):
        self.assertTrue(eradicate.comment_contains_code(
            '#return x'))

        self.assertFalse(eradicate.comment_contains_code(
            '#to return'))

    def test_comment_contains_code_with_multi_line(self):
        self.assertTrue(eradicate.comment_contains_code(
            '#def foo():'))

        self.assertTrue(eradicate.comment_contains_code(
            '#else:'))

        self.assertTrue(eradicate.comment_contains_code(
            '#  else  :  '))

        self.assertTrue(eradicate.comment_contains_code(
            '# "foo %d" % \\'))

        self.assertTrue(eradicate.comment_contains_code(
            '#elif True:'))

        self.assertTrue(eradicate.comment_contains_code(
            '#x = foo('))

        self.assertTrue(eradicate.comment_contains_code(
            '#except Exception:'))

        self.assertFalse(eradicate.comment_contains_code(
            '# this is = to that :('))

        self.assertFalse(eradicate.comment_contains_code(
            '#else'))

        self.assertFalse(eradicate.comment_contains_code(
            '#or else:'))

        self.assertFalse(eradicate.comment_contains_code(
            '#else True:'))

    def test_comment_contains_code_with_sentences(self):
        self.assertFalse(eradicate.comment_contains_code(
            '#code is good'))

    def test_comment_contains_code_with_encoding(self):
        self.assertFalse(eradicate.comment_contains_code(
            '# coding=utf-8'))

        self.assertFalse(eradicate.comment_contains_code(
            '#coding= utf-8'))

        self.assertFalse(eradicate.comment_contains_code(
            '# coding: utf-8'))

        self.assertFalse(eradicate.comment_contains_code(
            '# encoding: utf8'))

        self.assertTrue(eradicate.comment_contains_code(
            '# codings=utf-8'))

    def test_commented_out_code_line_numbers(self):
        self.assertEqual(
            [1, 3],
            list(eradicate.commented_out_code_line_numbers(
                """\
# print(5)
# This is a comment.
# x = 1

y = 1  # x = 3

# The below is another comment.
# 3 / 2 + 21
""")))

    def test_commented_out_code_line_numbers_with_errors(self):
        self.assertEqual(
            [1, 3],
            list(eradicate.commented_out_code_line_numbers(
                """\
# print(5)
# This is a comment.
# x = 1

y = 1  # x = 3

# The below is another comment.
# 3 / 2 + 21
def foo():
        1
    2
""")))

    def test_commented_out_code_line_numbers_with_with_statement(self):
        self.assertEqual(
            [1, 2],
            list(eradicate.commented_out_code_line_numbers("""\
# with open('filename', 'w') as out_file:
#     json.dump(objects, out_file)
#
""")))

    def test_commented_out_code_line_numbers_with_for_statement(self):
        self.assertEqual(
            [1, 2],
            list(eradicate.commented_out_code_line_numbers("""\
# for x in y:
#     oops = x.ham
""")))

    def test_filter_commented_out_code(self):
        self.assertEqual(
            """\
# This is a comment.

y = 1  # x = 3

# The below is another comment.
# 3 / 2 + 21
""",
            ''.join(eradicate.filter_commented_out_code(
                """\
# print(5)
# This is a comment.
# x = 1

y = 1  # x = 3

# The below is another comment.
# 3 / 2 + 21
# try:
#     x = 1
# finally:
#     x = 0
""")))

    def test_filter_commented_out_code_should_avoid_escaped_newlines(self):
        line = """\
if False: \\
# print(3)
    print(2)
    print(3)
"""
        self.assertEqual(
            line,
            ''.join(eradicate.filter_commented_out_code(line)))

    def test_filter_commented_out_code_with_larger_example(self):
        self.assertEqual(
            """\
# This is a comment.

y = 1  # x = 3

# The below is another comment.
# 3 / 2 + 21
""",
            ''.join(eradicate.filter_commented_out_code(
                """\
# print(5)
# This is a comment.
# x = 1

y = 1  # x = 3

# The below is another comment.
# 3 / 2 + 21
""")))

    def test_filter_commented_out_code_without_aggressive(self):
        code = """\
# iterate through choices inside of parenthesis (separated by '|'):

# if the Optional takes a value, format is:
#    -s ARGS, --long ARGS
"""
        self.assertEqual(
            code,
            ''.join(eradicate.filter_commented_out_code(code,
                                                        aggressive=False)))

    def test_filter_commented_out_code_with_annotation(self):
        self.assertEqual(
            '\n\n\n',
            ''.join(eradicate.filter_commented_out_code("""\
# class CommentedClass(object):
#     def __init__(self, prop: int) -> None:
#         self.property = prop

#     def __str__(self) -> str:
#         return self.__class__.__name__

#    def set_prop(self, prop: int):
#        self.prop = prop

#    def get_prop(self):
#        return self.prop
""")))

    def test_detect_encoding_with_bad_encoding(self):
        with temporary_file('# -*- coding: blah -*-\n') as filename:
            self.assertEqual('latin-1',
                             eradicate.detect_encoding(filename))


class SystemTests(unittest.TestCase):

    def test_diff(self):
        with temporary_file("""\
# x * 3 == False
# x is a variable
""") as filename:
            output_file = io.StringIO()
            eradicate.main(argv=['my_fake_program', filename],
                           standard_out=output_file,
                           standard_error=None)
            self.assertEqual("""\
@@ -1,2 +1 @@
-# x * 3 == False
 # x is a variable
""", '\n'.join(output_file.getvalue().split('\n')[2:]))

    def test_recursive(self):
        with temporary_directory() as directory:

            with temporary_file("""\
# x * 3 == False
# x is a variable
""", directory=directory):

                output_file = io.StringIO()
                eradicate.main(argv=['my_fake_program',
                                     '--recursive',
                                     directory],
                               standard_out=output_file,
                               standard_error=None)
                self.assertEqual("""\
@@ -1,2 +1 @@
-# x * 3 == False
 # x is a variable
""", '\n'.join(output_file.getvalue().split('\n')[2:]))

    def test_ignore_hidden_directories(self):
        with temporary_directory() as directory:
            with temporary_directory(prefix='.',
                                     directory=directory) as inner_directory:

                with temporary_file("""\
# x * 3 == False
# x is a variable
""", directory=inner_directory):

                    output_file = io.StringIO()
                    eradicate.main(argv=['my_fake_program',
                                         '--recursive',
                                         directory],
                                   standard_out=output_file,
                                   standard_error=None)
                    self.assertEqual(
                        '',
                        output_file.getvalue().strip())

    def test_in_place(self):
        with temporary_file("""\
# x * 3 == False
# x is a variable
""") as filename:
            output_file = io.StringIO()
            eradicate.main(argv=['my_fake_program', '--in-place', filename],
                           standard_out=output_file,
                           standard_error=None)
            with open(filename) as f:
                self.assertEqual("""\
# x is a variable
""", f.read())

    def test_with_missing_file(self):
        output_file = io.StringIO()
        ignore = StubFile()
        eradicate.main(argv=['my_fake_program', '--in-place', '.fake'],
                       standard_out=output_file,
                       standard_error=ignore)
        self.assertFalse(output_file.getvalue())

    def test_end_to_end(self):
        with temporary_file("""\
# x * 3 == False
# x is a variable
""") as filename:
            process = subprocess.Popen([sys.executable,
                                        './eradicate', filename],
                                       stdout=subprocess.PIPE)
            self.assertEqual("""\
@@ -1,2 +1 @@
-# x * 3 == False
 # x is a variable
""", '\n'.join(process.communicate()[0].decode().split('\n')[2:]))


@contextlib.contextmanager
def temporary_file(contents, directory='.', prefix=''):
    """Write contents to temporary file and yield it."""
    f = tempfile.NamedTemporaryFile(suffix='.py', prefix=prefix,
                                    delete=False, dir=directory)
    try:
        f.write(contents.encode())
        f.close()
        yield f.name
    finally:
        import os
        os.remove(f.name)


@contextlib.contextmanager
def temporary_directory(directory='.', prefix=''):
    """Create temporary directory and yield its path."""
    temp_directory = tempfile.mkdtemp(prefix=prefix, dir=directory)
    try:
        yield temp_directory
    finally:
        import shutil
        shutil.rmtree(temp_directory)


class StubFile(object):

    """Fake file that ignores everything."""

    def write(*_):
        """Ignore."""


if __name__ == '__main__':
    unittest.main()
