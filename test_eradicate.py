#!/usr/bin/env python

"""Test suite for eradicate."""

import unittest

import eradicate


class UnitTests(unittest.TestCase):

    def test_comment_contains_code(self):
        self.assertFalse(eradicate.comment_contains_code(
            ''))

        self.assertFalse(eradicate.comment_contains_code(
            'This is a real comment.'))

        self.assertTrue(eradicate.comment_contains_code(
            'x = 1'))

    def test_comment_contains_code_with_print(self):
        self.assertFalse(eradicate.comment_contains_code(
            'print'))

        self.assertTrue(eradicate.comment_contains_code(
            'print(1)'))

        self.assertTrue(eradicate.comment_contains_code(
            'print 1'))

    def test_normalize_line(self):
        self.assertEqual(
            '123',
            eradicate.normalize_line('print 123'))

        self.assertEqual(
            '(123)',
            eradicate.normalize_line('print(123)'))

        self.assertEqual(
            '( 123 )',
            eradicate.normalize_line('print ( 123 )'))

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


if __name__ == '__main__':
    unittest.main()
