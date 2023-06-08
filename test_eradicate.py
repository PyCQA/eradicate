#!/usr/bin/env python

"""Test suite for eradicate."""

from __future__ import unicode_literals

import contextlib
import io
import subprocess
import sys
import tempfile
import unittest
try:  # pragma: no cover
    import mock
except ModuleNotFoundError:  # pragma: no cover
    import unittest.mock as mock
import re

import eradicate


class UnitTests(unittest.TestCase):

    def test_comment_contains_code(self):
        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '#'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '# This is a (real) comment.'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '# 123'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '# 123.1'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '# 1, 2, 3'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            'x = 1  # x = 1'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '# pylint: disable=redefined-outer-name'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '# Issue #999: This is not code'))

        self.assertTrue(eradicate.Eradicator().comment_contains_code(
            '# x = 1'))

        self.assertTrue(eradicate.Eradicator().comment_contains_code(
            '#from foo import eradicate'))

        self.assertTrue(eradicate.Eradicator().comment_contains_code(
            '#import eradicate'))

        self.assertTrue(eradicate.Eradicator().comment_contains_code(
            '#"key": value,'))

        self.assertTrue(eradicate.Eradicator().comment_contains_code(
            '#"key": "value",'))

        self.assertTrue(eradicate.Eradicator().comment_contains_code(
            '#"key": 1 + 1,'))

        self.assertTrue(eradicate.Eradicator().comment_contains_code(
            "#'key': 1 + 1,"))

        self.assertTrue(eradicate.Eradicator().comment_contains_code(
            '#"key": {'))

        self.assertTrue(eradicate.Eradicator().comment_contains_code(
            '#}'))

        self.assertTrue(eradicate.Eradicator().comment_contains_code(
            '#} )]'))

        self.assertTrue(eradicate.Eradicator().comment_contains_code(
            '#},'))

    def test_comment_contains_code_with_print(self):
        self.assertTrue(eradicate.Eradicator().comment_contains_code(
            '#print'))

        self.assertTrue(eradicate.Eradicator().comment_contains_code(
            '#print(1)'))

        self.assertTrue(eradicate.Eradicator().comment_contains_code(
            '#print 1'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '#to print'))

    def test_comment_contains_code_with_return(self):
        self.assertTrue(eradicate.Eradicator().comment_contains_code(
            '#return x'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '#to return'))

    def test_comment_contains_code_with_multi_line(self):
        self.assertTrue(eradicate.Eradicator().comment_contains_code(
            '#def foo():'))

        self.assertTrue(eradicate.Eradicator().comment_contains_code(
            '#else:'))

        self.assertTrue(eradicate.Eradicator().comment_contains_code(
            '#  else  :  '))

        self.assertTrue(eradicate.Eradicator().comment_contains_code(
            '# "foo %d" % \\'))

        self.assertTrue(eradicate.Eradicator().comment_contains_code(
            '#elif True:'))

        self.assertTrue(eradicate.Eradicator().comment_contains_code(
            '#x = foo('))

        self.assertTrue(eradicate.Eradicator().comment_contains_code(
            '#except Exception:'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '# this is = to that :('))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '#else'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '#or else:'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '#else True:'))

    def test_comment_contains_code_with_sentences(self):
        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '#code is good'))

    def test_comment_contains_code_with_encoding(self):
        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '# coding=utf-8'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '#coding= utf-8'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '# coding: utf-8'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '# encoding: utf8'))

        self.assertTrue(eradicate.Eradicator().comment_contains_code(
            '# codings=utf-8'))

    def test_comment_contains_code_with_default_whitelist(self):
        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '# pylint: disable=A0123'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '# pylint:disable=A0123'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '# pylint: disable = A0123'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '# pylint:disable = A0123'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '# pyright: reportErrorName=true'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '# noqa'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '# NOQA'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '# noqa: A123'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '# noqa:A123'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '# nosec'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '# fmt: on'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '# fmt: off'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '# fmt:on'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '# fmt:off'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '# yapf: enable'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '# yapf: disable'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '# yapf:enable'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '# yapf:disable'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '# isort: on'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '# isort:on'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '# isort: off'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '# isort:off'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '# isort: skip'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '# isort:skip'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '# isort: skip_file'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '# isort:skip_file'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '# isort: split'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '# isort:split'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '# isort: dont-add-imports'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '# isort:dont-add-imports'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '# isort: dont-add-imports: ["import os"]'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '# isort:dont-add-imports: ["import os"]'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '# isort: dont-add-imports:["import os"]'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '# isort:dont-add-imports:["import os"]'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '# type: ignore'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '# type:ignore'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '# type: ignore[import]'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '# type:ignore[import]'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '# mypy: ignore-errors'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '# mypy: disable-error-code=['))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '# mypy: warn-unreachable, strict-optional'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '# TODO: Do that'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '# FIXME: Fix that'))

        self.assertFalse(eradicate.Eradicator().comment_contains_code(
            '# XXX: What ever'))


    def test_commented_out_code_line_numbers(self):
        self.assertEqual(
            [1, 3],
            list(eradicate.Eradicator().commented_out_code_line_numbers(
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
            list(eradicate.Eradicator().commented_out_code_line_numbers(
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
            list(eradicate.Eradicator().commented_out_code_line_numbers("""\
# with open('filename', 'w') as out_file:
#     json.dump(objects, out_file)
#
""")))

    def test_commented_out_code_line_numbers_with_for_statement(self):
        self.assertEqual(
            [1, 2],
            list(eradicate.Eradicator().commented_out_code_line_numbers("""\
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
            ''.join(eradicate.Eradicator().filter_commented_out_code(
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
            ''.join(eradicate.Eradicator().filter_commented_out_code(line)))

    def test_filter_commented_out_code_with_larger_example(self):
        self.assertEqual(
            """\
# This is a comment.

y = 1  # x = 3

# The below is another comment.
# 3 / 2 + 21
""",
            ''.join(eradicate.Eradicator().filter_commented_out_code(
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
            ''.join(eradicate.Eradicator().filter_commented_out_code(code,
                                                        aggressive=False)))

    def test_filter_commented_out_code_with_annotation(self):
        self.assertEqual(
            '\n\n\n',
            ''.join(eradicate.Eradicator().filter_commented_out_code("""\
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
                             eradicate.Eradicator().detect_encoding(filename))

    def test_extend_whitelist(self):
        eradicator = eradicate.Eradicator()
        eradicator.update_whitelist(["foo"], True)
        self.assertTrue(
            eradicator.WHITELIST_REGEX == re.compile(
                r'|'.join(list(eradicator.DEFAULT_WHITELIST) + ["foo"]), flags=re.IGNORECASE
            )
        )

    def test_update_whitelist(self):
        eradicator = eradicate.Eradicator()
        eradicator.update_whitelist(["foo"], False)
        self.assertTrue(eradicator.WHITELIST_REGEX == re.compile("foo", flags=re.IGNORECASE))


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

    def test_returns_error_code_if_requested(self):
        with temporary_file("""\
    # x * 3 == False
    # x is a variable
    """) as filename:
            output_file = io.StringIO()
            result = eradicate.main(argv=['my_fake_program', filename, "-e"],
                               standard_out=output_file,
                               standard_error=None)
            self.assertTrue(result)

    def test_returns_None_if_no_error_request(self):
        with temporary_file("""\
    # x * 3 == False
    # x is a variable
    """) as filename:
            output_file = io.StringIO()
            result = eradicate.main(argv=['my_fake_program', filename],
                               standard_out=output_file,
                               standard_error=None)
            self.assertTrue(result is None)

    def test_end_to_end(self):
        with temporary_file("""\
# x * 3 == False
# x is a variable
""") as filename:
            process = subprocess.Popen([sys.executable, '-m'
                                        'eradicate', filename],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                       universal_newlines=True)
            out, err = process.communicate()
            self.assertEqual("""\
@@ -1,2 +1 @@
-# x * 3 == False
 # x is a variable""",
            '\n'.join(out.splitlines()[2:]))
            self.assertEqual(err, '')

    def test_whitelist(self):
        mock_update = mock.Mock()
        with mock.patch.object(eradicate.Eradicator, 'update_whitelist', mock_update):
            with temporary_file("# empty") as filename:
                result = eradicate.main(argv=['my_fake_program', '--whitelist', 'foo# bar', filename],
                                   standard_out=None,
                                   standard_error=None)
            self.assertTrue(result is None)
            mock_update.assert_called_once_with(["foo", " bar"], False)

    def test_whitelist_extend(self):
        mock_update = mock.Mock()
        with mock.patch.object(eradicate.Eradicator, 'update_whitelist', mock_update):
            with temporary_file("# empty") as filename:
                result = eradicate.main(argv=['my_fake_program', '--whitelist-extend', 'foo #bar', filename],
                                   standard_out=None,
                                   standard_error=None)
            self.assertTrue(result is None)
            mock_update.assert_called_once_with(["foo ", "bar"], True)


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
