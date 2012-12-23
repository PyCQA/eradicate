#!/usr/bin/env python

"""Test suite for eradicate."""

import contextlib
from io import StringIO
import tempfile
import unittest

import eradicate


try:
    unicode
except NameError:
    unicode = str


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

        self.assertTrue(eradicate.comment_contains_code(
            '# x = 1'))

    def test_comment_contains_code_with_print(self):
        self.assertTrue(eradicate.comment_contains_code(
            '#print'))

        self.assertTrue(eradicate.comment_contains_code(
            '#print(1)'))

        self.assertTrue(eradicate.comment_contains_code(
            '#print 1'))

    def test_comment_contains_code_with_multi_line(self):
        self.assertTrue(eradicate.comment_contains_code(
            '#def foo():'))

        self.assertTrue(eradicate.comment_contains_code(
            '#else:'))

        self.assertFalse(eradicate.comment_contains_code(
            '#else'))

    def test_comment_contains_code_with_sentences(self):
        self.assertFalse(eradicate.comment_contains_code(
            '#code is good'))

    def test_commented_out_code_line_numbers(self):
        self.assertEqual(
            [1, 3],
            list(eradicate.commented_out_code_line_numbers(
                unicode("""\
# print(5)
# This is a comment.
# x = 1

y = 1  # x = 3

# The below is another comment.
# 3 / 2 + 21
"""))))

    def test_commented_out_code_line_numbers_with_errors(self):
        self.assertEqual(
            [1, 3],
            list(eradicate.commented_out_code_line_numbers(
                unicode("""\
# print(5)
# This is a comment.
# x = 1

y = 1  # x = 3

# The below is another comment.
# 3 / 2 + 21
def foo():
        1
    2
"""))))

    def test_filter_commented_out_code(self):
        self.assertEqual(
            """\
# This is a comment.

y = 1  # x = 3

# The below is another comment.
# 3 / 2 + 21
""",
            ''.join(eradicate.filter_commented_out_code(
                unicode("""\
# print(5)
# This is a comment.
# x = 1

y = 1  # x = 3

# The below is another comment.
# 3 / 2 + 21
"""))))

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
            output_file = StringIO()
            eradicate.main(argv=['my_fake_program', filename],
                           standard_out=output_file)
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

                output_file = StringIO()
                eradicate.main(argv=['my_fake_program',
                                     '--recursive',
                                     directory],
                               standard_out=output_file)
                self.assertEqual("""\
@@ -1,2 +1 @@
-# x * 3 == False
 # x is a variable
""", '\n'.join(output_file.getvalue().split('\n')[2:]))

    def test_in_place(self):
        with temporary_file("""\
# x * 3 == False
# x is a variable
""") as filename:
            output_file = StringIO()
            eradicate.main(argv=['my_fake_program', '--in-place', filename],
                           standard_out=output_file)
            with open(filename) as f:
                self.assertEqual("""\
# x is a variable
""", f.read())

    def test_end_to_end(self):
        with temporary_file("""\
# x * 3 == False
# x is a variable
""") as filename:
            import subprocess
            process = subprocess.Popen(['./eradicate', filename],
                                       stdout=subprocess.PIPE)
            self.assertEqual("""\
@@ -1,2 +1 @@
-# x * 3 == False
 # x is a variable
""", '\n'.join(process.communicate()[0].decode('utf-8').split('\n')[2:]))


@contextlib.contextmanager
def temporary_file(contents, directory='.'):
    """Write contents to temporary file and yield it."""
    f = tempfile.NamedTemporaryFile(suffix='.py', delete=False, dir=directory)
    try:
        f.write(contents.encode('utf8'))
        f.close()
        yield f.name
    finally:
        import os
        os.remove(f.name)


@contextlib.contextmanager
def temporary_directory(directory='.'):
    """Create temporary directory and yield its path."""
    temp_directory = tempfile.mkdtemp(dir=directory)
    try:
        yield temp_directory
    finally:
        import shutil
        shutil.rmtree(temp_directory)


if __name__ == '__main__':
    unittest.main()
