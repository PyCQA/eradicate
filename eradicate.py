"""Remove commented out Python code."""

from io import StringIO
import re
import tokenize


def normalize_line(line):
    """Normalize before checking for code."""
    line = line.lstrip(' \t\v\n#').strip()

    return re.sub(r'print\b\s*', '', line)


def comment_contains_code(line):
    """Return True comment contains code."""
    line = normalize_line(line)
    if not line:
        return False

    try:
        compile(line, '<string>', 'exec')
        return True
    except (SyntaxError, TypeError, UnicodeDecodeError):
        return False


def commented_out_code_line_numbers(source):
    """Yield line numbers of commented-out code."""
    sio = StringIO(source)
    formatted = ''
    for token in tokenize.generate_tokens(sio.readline):
        token_type = token[0]
        start_row = token[2][0]
        line = token[4]

        if token_type == tokenize.COMMENT and comment_contains_code(line):
            yield start_row

    return formatted


def filter_commented_out_code(source):
    """Yield code with commented out code removed."""
    marked_lines = list(commented_out_code_line_numbers(source))
    sio = StringIO(source)
    for line_number, line in enumerate(sio.readlines(), start=1):
        if line_number not in marked_lines:
            yield line


def open_with_encoding(filename, encoding, mode='r'):
    """Return opened file with a specific encoding."""
    import io
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
