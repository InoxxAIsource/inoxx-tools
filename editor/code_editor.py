from rich.syntax import Syntax
from rich.text import Text
from rich.panel import Panel
from pygments.lexers import PythonLexer
from utils.error_detector import ErrorDetector
from ai.code_assistant import CodeAssistant
import json

class CodeEditor:
    def __init__(self):
        self.current_file = None
        self.content = ""
        self.cursor_pos = (1, 1)  # (line, column)
        self.error_detector = ErrorDetector()
        self.code_assistant = CodeAssistant()
        self.scroll_offset = 0
        self.suggestions = []
        self.lexer = PythonLexer()
        self.editing_mode = "insert"  # insert or command
        print("CodeEditor initialized")

    def load_file(self, filepath):
        try:
            with open(filepath, 'r') as f:
                self.content = f.read()
            self.current_file = filepath
            self.cursor_pos = (1, 1)
            self.scroll_offset = 0
            self.check_for_errors()
            print(f"Loaded file: {filepath}")
            return "File loaded successfully"
        except Exception as e:
            error_msg = f"Error loading file: {str(e)}"
            print(error_msg)
            return error_msg

    def save_current_file(self):
        if not self.current_file:
            return "No file is currently open"
        try:
            with open(self.current_file, 'w') as f:
                f.write(self.content)
            print(f"Saved file: {self.current_file}")
            return "File saved successfully"
        except Exception as e:
            error_msg = f"Error saving file: {str(e)}"
            print(error_msg)
            return error_msg

    def move_cursor(self, direction):
        old_pos = self.cursor_pos
        lines = self.content.split('\n')
        current_line, current_col = self.cursor_pos

        if direction == 'up' and current_line > 1:
            self.cursor_pos = (current_line - 1, min(current_col, len(lines[current_line - 2]) + 1))
        elif direction == 'down' and current_line < len(lines):
            self.cursor_pos = (current_line + 1, min(current_col, len(lines[current_line]) + 1))
        elif direction == 'left' and current_col > 1:
            self.cursor_pos = (current_line, current_col - 1)
        elif direction == 'right':
            if current_col <= len(lines[current_line - 1]):
                self.cursor_pos = (current_line, current_col + 1)

        # Adjust scroll if cursor moves out of view
        if current_line - self.scroll_offset < 2:
            self.scroll_offset = max(0, current_line - 2)
        elif current_line - self.scroll_offset > 18:
            self.scroll_offset = current_line - 18

        print(f"Cursor moved {direction}: {old_pos} -> {self.cursor_pos}")

    def insert_text(self, text):
        lines = self.content.split('\n')
        line_num, col_num = self.cursor_pos

        if not lines:
            self.content = text
            self.cursor_pos = (1, len(text) + 1)
            print(f"Inserted text in empty file: '{text}'")
            return

        current_line = lines[line_num - 1]
        new_line = current_line[:col_num - 1] + text + current_line[col_num - 1:]
        lines[line_num - 1] = new_line
        self.content = '\n'.join(lines)
        self.cursor_pos = (line_num, col_num + len(text))
        print(f"Inserted text at {self.cursor_pos}: '{text}'")
        self.check_for_errors()

    def delete_text(self, backspace=True):
        if not self.content:
            return

        lines = self.content.split('\n')
        line_num, col_num = self.cursor_pos

        if backspace and col_num > 1:
            current_line = lines[line_num - 1]
            new_line = current_line[:col_num - 2] + current_line[col_num - 1:]
            lines[line_num - 1] = new_line
            self.cursor_pos = (line_num, col_num - 1)
            print(f"Backspace at {self.cursor_pos}")
        elif not backspace and col_num <= len(lines[line_num - 1]):
            current_line = lines[line_num - 1]
            new_line = current_line[:col_num - 1] + current_line[col_num:]
            lines[line_num - 1] = new_line
            print(f"Delete at {self.cursor_pos}")

        self.content = '\n'.join(lines)
        self.check_for_errors()

    def check_for_errors(self):
        """Check for code errors and get AI suggestions for fixes"""
        errors = self.error_detector.check_code(self.content)
        if errors:
            print(f"Found {len(errors)} errors in code")
            for error in errors:
                print(f"Error at line {error.get('line')}: {error.get('message')}")

            # Get AI suggestions for fixing errors
            fixes = self.code_assistant.get_code_fixes(self.content, errors)
            if isinstance(fixes, dict) and 'fixes' in fixes:
                print("AI suggestions for fixes:")
                for i, (fix, explanation) in enumerate(zip(fixes['fixes'], fixes['explanations']), 1):
                    print(f"{i}. {explanation}")
        return errors

    def get_completion_suggestions(self):
        """Get AI-powered code completion suggestions"""
        if not self.content:
            return []

        line_num, col_num = self.cursor_pos
        suggestions = self.code_assistant.get_suggestions(self.content, (line_num, col_num))
        print(f"Got {len(suggestions)} completion suggestions")
        return suggestions

    def analyze_current_code(self):
        """Get AI analysis of current code"""
        if not self.content:
            return "No code to analyze"

        analysis = self.code_assistant.analyze_code(self.content)
        if isinstance(analysis, dict):
            if 'error' in analysis:
                return f"Error analyzing code: {analysis['error']}"
            return f"Analysis: {analysis.get('analysis')}\nSuggestions: {analysis.get('suggestions')}"
        return "Invalid analysis result"

    def get_documentation_at_cursor(self):
        """Get AI-generated documentation for the code element at cursor"""
        if not self.content:
            return "No code to document"

        # Extract current function or class definition
        lines = self.content.split('\n')
        current_line = self.cursor_pos[0] - 1

        # Simple extraction of current code block
        start_line = current_line
        while start_line > 0 and not lines[start_line].startswith(('def ', 'class ')):
            start_line -= 1

        if start_line < 0:
            return "No documentable element found at cursor"

        # Extract the code block
        end_line = start_line
        indent = len(lines[start_line]) - len(lines[start_line].lstrip())
        while end_line < len(lines) and (not lines[end_line].strip() or 
                                       len(lines[end_line]) - len(lines[end_line].lstrip()) >= indent):
            end_line += 1

        code_element = '\n'.join(lines[start_line:end_line])
        docs = self.code_assistant.get_documentation(code_element)

        if isinstance(docs, dict):
            if 'error' in docs:
                return f"Error generating documentation: {docs['error']}"
            return f"Documentation:\n{json.dumps(docs, indent=2)}"
        return "Invalid documentation result"


    def render(self):
        try:
            if not self.content:
                return Text("No file open", style="italic")

            # Calculate visible portion based on scroll offset
            lines = self.content.split('\n')
            visible_lines = lines[self.scroll_offset:self.scroll_offset + 20]
            visible_content = '\n'.join(visible_lines)

            # Create syntax highlighted content
            syntax = Syntax(
                visible_content,
                "python",
                theme="monokai",
                line_numbers=True,
                start_line=self.scroll_offset + 1,
                highlight_lines={self.cursor_pos[0] - self.scroll_offset}
            )

            # Add cursor indicator
            cursor_line = self.cursor_pos[0] - self.scroll_offset
            if 1 <= cursor_line <= len(visible_lines):
                print(f"Cursor visible at line {cursor_line}")
                return syntax

            return syntax
        except Exception as e:
            error_msg = f"Error rendering code: {str(e)}"
            print(error_msg)
            return Text(error_msg, style="red")