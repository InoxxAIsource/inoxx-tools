import os
import json
from openai import OpenAI

class CodeAssistant:
    def __init__(self):
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        self.model = "gpt-4o"
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    def get_suggestions(self, code_context, cursor_position):
        """Get code completion suggestions based on context"""
        if not self.client:
            return ["AI assistance not available - API key not set"]

        try:
            line_num, col_num = cursor_position
            lines = code_context.split('\n')
            current_line = lines[line_num - 1] if line_num <= len(lines) else ""
            context_before = current_line[:col_num]

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a Python code completion assistant. 
                        Provide short, relevant code suggestions based on context.
                        Focus on completing the current statement or expression.
                        Return a JSON object with an array of suggestions."""
                    },
                    {
                        "role": "user",
                        "content": f"Complete this Python code:\nContext before cursor: {context_before}\nFull line: {current_line}"
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=150,
                temperature=0.7,
                n=3
            )

            result = json.loads(response.choices[0].message.content)
            return result.get("suggestions", ["No valid suggestions available"])
        except Exception as e:
            return [f"Error getting suggestions: {str(e)}"]

    def analyze_code(self, code):
        """Analyze code and provide improvement suggestions"""
        if not self.client:
            return "AI analysis not available - API key not set"

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """Analyze this Python code and provide:
                        1. Code quality assessment
                        2. Potential bugs and issues
                        3. Performance improvements
                        4. Best practices recommendations
                        Return in JSON format with 'analysis' and 'suggestions' keys."""
                    },
                    {
                        "role": "user",
                        "content": code
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=500
            )

            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {"error": str(e)}

    def get_documentation(self, code_element):
        """Generate documentation for code elements"""
        if not self.client:
            return "AI documentation not available - API key not set"

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """Generate ONLY a JSON object with these exact keys and nothing else:
                        {
                            "description": "Brief description of what the code does",
                            "params": [{"name": "param_name", "type": "param_type", "description": "param description"}],
                            "returns": {"type": "return_type", "description": "description of return value"},
                            "examples": ["example1", "example2"]
                        }
                        """
                    },
                    {
                        "role": "user",
                        "content": code_element
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=300,
                temperature=0.2  # Even lower temperature for strict JSON output
            )

            print(f"Raw documentation response: {response.choices[0].message.content}")  # Debug log
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Failed content: {response.choices[0].message.content}")
            return {
                "error": "Documentation format error",
                "description": "Could not parse documentation output",
                "params": [],
                "returns": {"type": "unknown", "description": "Error generating documentation"},
                "examples": []
            }
        except Exception as e:
            print(f"Documentation generation error: {e}")
            return {
                "error": str(e),
                "description": "Failed to generate documentation",
                "params": [],
                "returns": {"type": "unknown", "description": "Error in documentation generation"},
                "examples": []
            }

    def get_code_fixes(self, code, errors):
        """Get suggestions for fixing code errors"""
        if not self.client:
            return "AI fixes not available - API key not set"

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """Provide suggestions to fix the code errors.
                        Return a JSON object with:
                        - fixes: array of suggested fixes
                        - explanations: array of fix explanations"""
                    },
                    {
                        "role": "user",
                        "content": f"Code:\n{code}\n\nErrors:\n{json.dumps(errors, indent=2)}"
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=400
            )

            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {"error": str(e)}