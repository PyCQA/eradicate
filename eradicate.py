# Copyright (C) 2012-2015 Steven Myint
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""Removes commented-out Python code."""

from __future__ import print_function
from __future__ import unicode_literals

import difflib
import io
import os
import re
import tokenize

__version__ = '1.0'


MULTILINE_ASSIGNMENT_REGEX = re.compile(r'^\s*\w+\s*=.*[(\[{]$')
PARTIAL_DICTIONARY_REGEX = re.compile(r'^\s*[\'"]\w+[\'"]\s*:.+[,{]\s*$')


def comment_contains_code(line, aggressive=True):
    """Return True comment contains code."""
    line = line.lstrip()
    if not line.startswith('#'):
        return False

    line = line.lstrip(' \t\v\n#').strip()

    # Ignore non-comment related hashes. For example, "# Issue #999".
    if re.search('#[0-9]', line):
        return False

    if line.startswith('pylint:'):
        return False

    if re.match(r'.*?coding[:=][ \t]*([-_.a-zA-Z0-9]+)', line):
        return False

    # Check that this is possibly code.
    for symbol in list('()[]{}:=%') + ['print', 'return', 'break', 'continue',
                                       'import']:
        if symbol in line:
            break
    else:
        return False

    if multiline_case(line, aggressive=aggressive):
        return True

    symbol_list = [r'elif\s+.*', 'else', 'try',
                   'finally', r'except\s+.*']
    if aggressive:
        symbol_list.append(r'if\s+.*')

    for symbol in symbol_list:
        if re.match(r'^\s*' + symbol + r'\s*:\s*$', line):
            return True

    line = re.sub(r'^(print|return)\b\s*', '', line)

    if re.match(PARTIAL_DICTIONARY_REGEX, line):
        return True

    try:
        compile(line, '<string>', 'exec')
        return True
    except (SyntaxError, TypeError, UnicodeDecodeError):
        return False


def multiline_case(line, aggressive=True):
    """Return True if line is probably part of some multiline code."""
    if aggressive:
        for ending in ')]}':
            if line.endswith(ending + ':'):
                return True

            if line.strip() == ending + ',':
                return True

        # Check whether a function/method definition with return value
        # annotation
        if re.search(r"def .+\)[\s]+->[\s]+[a-zA-Z_][a-zA-Z0-9_]*:$", line):
            return True

        # Check weather a with statement
        if re.search(r"with .+ as [a-zA-Z_][a-zA-Z0-9_]*:$", line):
            return True

        # Check weather a for statement
        if re.search(r"for [a-zA-Z_][a-zA-Z0-9_]* in .+:$", line):
            return True

    if line.endswith('\\'):
        return True

    if re.match(MULTILINE_ASSIGNMENT_REGEX, line):
        return True

    if re.match(r'^[()\[\]{}\s]+$', line):
        return True

    return False


def commented_out_code_line_numbers(source, aggressive=True):
    """Yield line numbers of commented-out code."""
    sio = io.StringIO(source)
    try:
        for token in tokenize.generate_tokens(sio.readline):
            token_type = token[0]
            start_row = token[2][0]
            line = token[4]

            if (token_type == tokenize.COMMENT and
                    line.lstrip().startswith('#') and
                    comment_contains_code(line, aggressive)):
                yield start_row
    except (tokenize.TokenError, IndentationError):
        pass


def filter_commented_out_code(source, aggressive=True):
    """Yield code with commented out code removed."""
    marked_lines = list(commented_out_code_line_numbers(source,
                                                        aggressive))
    sio = io.StringIO(source)
    previous_line = ''
    for line_number, line in enumerate(sio.readlines(), start=1):
        if (line_number not in marked_lines or
                previous_line.rstrip().endswith('\\')):
            yield line
        previous_line = line


def fix_file(filename, args, standard_out):
    """Run filter_commented_out_code() on file."""
    encoding = detect_encoding(filename)
    with open_with_encoding(filename, encoding=encoding) as input_file:
        source = input_file.read()

    filtered_source = ''.join(filter_commented_out_code(source,
                                                        args.aggressive))

    if source != filtered_source:
        if args.in_place:
            with open_with_encoding(filename, mode='w',
                                    encoding=encoding) as output_file:
                output_file.write(filtered_source)
        else:
            diff = difflib.unified_diff(
                source.splitlines(),
                filtered_source.splitlines(),
                'before/' + filename,
                'after/' + filename,
                lineterm='')
            standard_out.write('\n'.join(list(diff) + ['']))


def open_with_encoding(filename, encoding, mode='r'):
    """Return opened file with a specific encoding."""
    return io.open(filename, mode=mode, encoding=encoding,
                   newline='')  # Preserve line endings


def detect_encoding(filename):
    """Return file encoding."""
    try:
        with open(filename, 'rb') as input_file:
            from lib2to3.pgen2 import tokenize as lib2to3_tokenize
            encoding = lib2to3_tokenize.detect_encoding(input_file.readline)[0]

            # Check for correctness of encoding.
            with open_with_encoding(filename, encoding) as input_file:
                input_file.read()

        return encoding
    except (SyntaxError, LookupError, UnicodeDecodeError):
        return 'latin-1'


def main(argv, standard_out, standard_error):
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description=__doc__, prog='eradicate')
    parser.add_argument('-i', '--in-place', action='store_true',
                        help='make changes to files instead of printing diffs')
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='drill down directories recursively')
    parser.add_argument('-a', '--aggressive', action='store_true',
                        help='make more aggressive changes; '
                             'this may result in false positives')
    parser.add_argument('--version', action='version',
                        version='%(prog)s ' + __version__)
    parser.add_argument('files', nargs='+', help='files to format')

    args = parser.parse_args(argv[1:])

    filenames = list(set(args.files))
    while filenames:
        name = filenames.pop(0)
        if args.recursive and os.path.isdir(name):
            for root, directories, children in os.walk('{}'.format(name)):
                filenames += [os.path.join(root, f) for f in children
                              if f.endswith('.py') and
                              not f.startswith('.')]
                directories[:] = [d for d in directories
                                  if not d.startswith('.')]
        else:
            try:
                fix_file(name, args=args, standard_out=standard_out)
            except IOError as exception:
                print('{}'.format(exception), file=standard_error)
