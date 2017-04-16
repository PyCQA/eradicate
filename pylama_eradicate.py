"""
pylama integration for eradicate.

Based on: https://github.com/timothycrosley/isort
"""

from io import StringIO

from pylama.lint import Linter as BaseLinter

from eradicate import fix_file


class Linter(BaseLinter):

    def allow(self, path):
        """Determine if this path should be linted."""
        return path.endswith('.py')

    def run(self, path, **meta):
        """Lint the file. Return an array of error dicts if appropriate."""

        out = StringIO()

        class Args():
            in_place = False
        args = Args()

        fix_file(path, args, out)

        out.seek(0)
        errors = out.read()

        if errors:
            return errors
        else:
            return []
