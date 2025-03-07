from pygments.lexers import PythonLexer
from pygments.token import Token
import ast

class SyntaxHelper:
    def __init__(self):
        self.lexer = PythonLexer()

    def get_token_at_position(self, code, position):
        tokens = list(self.lexer.get_tokens(code))
        current_pos = 0
        
        for token_type, token_value in tokens:
            token_length = len(token_value)
            if current_pos <= position < current_pos + token_length:
                return token_type, token_value
            current_pos += token_length
        
        return None, None

    def get_context_info(self, code, position):
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if hasattr(node, 'lineno'):
                    if node.lineno == position[0]:
                        return {
                            'type': type(node).__name__,
                            'line': node.lineno,
                            'col': node.col_offset
                        }
        except:
            pass
        return None

    def get_completion_context(self, code, position):
        try:
            lines = code.split('\n')
            current_line = lines[position[0] - 1][:position[1]]
            
            # Check for method completion
            if '.' in current_line:
                obj = current_line.rstrip().split('.')[-2]
                return {'type': 'method', 'object': obj}
            
            # Check for function parameters
            if '(' in current_line:
                func = current_line.split('(')[0].strip()
                return {'type': 'parameter', 'function': func}
            
        except Exception:
            pass
        
        return {'type': 'general'}
