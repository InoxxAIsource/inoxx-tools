import ast
import pyflakes.api as pyflakes
import io
from pygments.lexers import PythonLexer
from pygments.token import Token, Error

class ErrorDetector:
    def __init__(self):
        self.lexer = PythonLexer()

    def check_code(self, code):
        errors = []

        # Syntax errors
        try:
            ast.parse(code)
        except SyntaxError as e:
            errors.append({
                'type': 'syntax',
                'line': e.lineno,
                'offset': e.offset,
                'message': str(e)
            })
            return errors

        # Pyflakes errors
        reporter = ErrorCollector()
        pyflakes.check(code, 'code', reporter)
        errors.extend(reporter.get_errors())

        # Token-level errors
        try:
            tokens = list(self.lexer.get_tokens(code))
            for i, (token_type, value) in enumerate(tokens):
                if token_type in Token.Error:
                    line = self._get_line_number(tokens, i)
                    errors.append({
                        'type': 'token',
                        'line': line,
                        'message': f'Invalid token: {value}'
                    })
        except Exception as e:
            errors.append({
                'type': 'tokenizer',
                'line': 0,
                'message': str(e)
            })

        return errors

    def _get_line_number(self, tokens, index):
        line = 1
        for i in range(index):
            if tokens[i][1] == '\n':
                line += 1
        return line

class ErrorCollector:
    def __init__(self):
        self.warnings = []
        self._stdout = io.StringIO()

    def flake(self, message):
        self.warnings.append(message)

    def get_errors(self):
        return [
            {
                'type': 'pyflakes',
                'line': warning.lineno,
                'message': warning.message % warning.message_args
            }
            for warning in self.warnings
        ]

    # Implementing required Reporter interface methods
    def unexpectedError(self, filename, message):
        self._stdout.write(f"Unexpected error in {filename}: {message}\n")

    def syntaxError(self, filename, message, lineno, offset, text):
        self._stdout.write(f"Syntax error in {filename}:{lineno}: {message}\n")

    def get_output(self):
        return self._stdout.getvalue()