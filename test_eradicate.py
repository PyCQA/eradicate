#!/usr/bin/env python

"""Test suite for eradicate."""

import contextlib
from io import StringIO
import unittest

import eradicate


class UnitTests(unittest.TestCase):

    def test_comment_contains_code(self):
        self.assertFalse(eradicate.comment_contains_code(
            '#'))

        self.assertFalse(eradicate.comment_contains_code(
            '# This is a real comment.'))

        self.assertFalse(eradicate.comment_contains_code(
            '# 123'))

        self.assertTrue(eradicate.comment_contains_code(
            '# x = 1'))

    def test_comment_contains_code_with_print(self):
        self.assertFalse(eradicate.comment_contains_code(
            'print'))

        self.assertTrue(eradicate.comment_contains_code(
            'print(1)'))

        self.assertTrue(eradicate.comment_contains_code(
            'print 1'))

    def test_commented_out_code_line_numbers(self):
        self.assertEqual(
            [1, 3, 8],
            list(eradicate.commented_out_code_line_numbers(
                """\
# print(5)
# This is a comment.
# x = 1

y = 1

# Another comment.
# 3 / 2 + 21
""")))

    def test_filter_commented_out_code(self):
        self.assertEqual(
                """\
# This is a comment.

y = 1

# Another comment.
""",
            ''.join(eradicate.filter_commented_out_code(
                """\
# print(5)
# This is a comment.
# x = 1

y = 1

# Another comment.
# 3 / 2 + 21
""")))


@contextlib.contextmanager
def temporary_file(contents):
    """Write contents to temporary file and yield it."""
    import tempfile
    f = tempfile.NamedTemporaryFile(suffix='.py', delete=False, dir='.')
    try:
        f.write(contents.encode('utf8'))
        f.close()
        yield f.name
    finally:
        import os
        os.remove(f.name)


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


if __name__ == '__main__':
    unittest.main()
