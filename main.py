#!/usr/bin/env python3
import os
import sys
import ast
import json
from flask import Flask, render_template, jsonify, request, send_from_directory
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich.panel import Panel
from editor.code_editor import CodeEditor
from editor.file_browser import FileBrowser
from editor.project_manager import ProjectManager
from utils.snippet_manager import SnippetManager
from blockchain.blockchain_core import Blockchain, Block
from blockchain.smart_contracts import SmartContractDeveloper
from utils.debugger import DebuggerController

app = Flask(__name__)
ide = None

class IDE:
    def __init__(self, test_mode=False):
        self.code_editor = CodeEditor()
        self.file_browser = FileBrowser()
        self.project_manager = ProjectManager()
        self.snippet_manager = SnippetManager()
        self.blockchain = Blockchain()
        self.contract_developer = SmartContractDeveloper()
        self.debugger = DebuggerController()
        if not test_mode:
            self.console = Console()
            self.layout = Layout()
            self.setup_layout()
            self.active_panel = "editor"
            print("IDE initialized with default editor focus")

    def setup_layout(self):
        if not hasattr(self, 'layout'):
            return
        self.layout.split(
            Layout(name="header", size=3),
            Layout(name="main")
        )
        self.layout["main"].split_row(
            Layout(name="sidebar", ratio=1),
            Layout(name="editor", ratio=4)
        )
        self.layout["sidebar"].split(
            Layout(name="file_browser", ratio=2),
            Layout(name="snippets", ratio=1)
        )
        print("Layout setup completed")

    def update_layout(self):
        try:
            header_text = Text("AI-Assisted Python IDE", style="bold white")
            header_text.append(" | ", style="white")
            header_text.append("Keys: ", style="cyan")
            header_text.append("[q]uit ", style="yellow")
            header_text.append("[o]pen ", style="yellow")
            header_text.append("[s]ave ", style="yellow")
            header_text.append("[tab] switch panel", style="yellow")
            header_text.append("[a]nalyze ", style="yellow")
            header_text.append("[d]ocument ", style="yellow")
            self.layout["header"].update(Panel(header_text, border_style="blue"))

            self.layout["file_browser"].update(Panel(
                self.file_browser.render(),
                title="[bold]Files" + (" [focused]" if self.active_panel == "file_browser" else ""),
                border_style="green" if self.active_panel == "file_browser" else "white"
            ))

            editor_title = f"[bold]{self.code_editor.current_file or 'No File Open'}"
            editor_title += " [focused]" if self.active_panel == "editor" else ""
            self.layout["editor"].update(Panel(
                self.code_editor.render(),
                title=editor_title,
                border_style="yellow" if self.active_panel == "editor" else "white"
            ))

            snippets = self.snippet_manager.list_snippets()
            if isinstance(snippets, list):
                snippet_text = "\n".join([
                    f"• {s.get('name', 'Unnamed')} - {s.get('description', '')[:30]}"
                    for s in snippets[:5]
                ]) or "No snippets available"
            else:
                snippet_text = "Error loading snippets"

            self.layout["snippets"].update(Panel(
                Text(snippet_text),
                title="[bold]Code Snippets" + (" [focused]" if self.active_panel == "snippets" else ""),
                border_style="magenta" if self.active_panel == "snippets" else "white"
            ))
        except Exception as e:
            print(f"\nError updating layout: {str(e)}")

    def handle_input(self):
        try:
            key = self.console.input() if hasattr(self, 'console') else ""
            print(f"\nReceived key input: {key}")

            if key.lower() == 'q':
                raise KeyboardInterrupt()
            elif key.lower() == 'o':
                print("Opening file...")
                self.handle_file_open()
            elif key.lower() == 's':
                print("Saving file...")
                self.handle_file_save()
            elif key == '\t':
                print("Switching focus...")
                self.cycle_focus()
            elif key == 'a':
                if self.active_panel == "editor":
                    analysis = self.code_editor.analyze_current_code()
                    self.console.print("\nCode Analysis:", style="bold cyan") if hasattr(self, 'console') else print("\nCode Analysis:")
                    self.console.print(analysis) if hasattr(self, 'console') else print(analysis)

            elif key == 'd':
                if self.active_panel == "editor":
                    docs = self.code_editor.get_documentation_at_cursor()
                    self.console.print("\nDocumentation:", style="bold green") if hasattr(self, 'console') else print("\nDocumentation:")
                    self.console.print(docs) if hasattr(self, 'console') else print(docs)
            elif self.active_panel == "editor":
                print(f"Handling editor input: {key}")
                self.handle_editor_input(key)
        except Exception as e:
            print(f"\nError handling input: {str(e)}")

    def cycle_focus(self):
        panels = ["editor", "file_browser", "snippets"]
        current_index = panels.index(self.active_panel)
        self.active_panel = panels[(current_index + 1) % len(panels)]
        print(f"Focus switched to: {self.active_panel}")

    def handle_editor_input(self, key):
        if key in ['up', 'down', 'left', 'right']:
            print(f"Moving cursor: {key}")
            self.code_editor.move_cursor(key)
        elif len(key) == 1:
            print(f"Inserting character: {key}")
            self.code_editor.insert_text(key)
        elif key == 'backspace':
            print("Deleting character (backspace)")
            self.code_editor.delete_text(backspace=True)
        elif key == 'delete':
            print("Deleting character (delete)")
            self.code_editor.delete_text(backspace=False)

    def handle_file_open(self):
        files = self.file_browser.get_python_files()
        if not files:
            self.console.print("\nNo Python files found", style="yellow") if hasattr(self, 'console') else print("\nNo Python files found")
            return

        self.console.print("\nAvailable Python files:", style="green") if hasattr(self, 'console') else print("\nAvailable Python files:")
        for i, file in enumerate(files, 1):
            self.console.print(f"{i}: {file}") if hasattr(self, 'console') else print(f"{i}: {file}")

        try:
            choice = self.console.input("\nEnter file number to open: ") if hasattr(self, 'console') else input("\nEnter file number to open: ")
            file_index = int(choice) - 1
            if 0 <= file_index < len(files):
                result = self.code_editor.load_file(files[file_index])
                self.project_manager.add_recent_file(files[file_index])
                self.console.print(f"\n{result}", style="green") if hasattr(self, 'console') else print(f"\n{result}")
                self.active_panel = "editor"
                print(f"Opened file: {files[file_index]}")
            else:
                self.console.print("\nInvalid file number", style="red") if hasattr(self, 'console') else print("\nInvalid file number")
        except ValueError:
            self.console.print("\nInvalid input", style="red") if hasattr(self, 'console') else print("\nInvalid input")

    def handle_file_save(self):
        result = self.code_editor.save_current_file()
        style = "green" if "successfully" in result.lower() else "red"
        self.console.print(f"\n{result}", style=style) if hasattr(self, 'console') else print(f"\n{result}")
        print(f"Save result: {result}")

    def run(self):
        try:
            print("Starting IDE...")
            if hasattr(self, 'layout'):
                with Live(self.layout, screen=True, refresh_per_second=10) as live:
                    while True:
                        self.update_layout()
                        self.handle_input()
                        live.refresh()
        except KeyboardInterrupt:
            print("\nExiting IDE...")
        except Exception as e:
            print(f"\nError running IDE: {str(e)}")

    def test_ai_features(self):
        print("\nTesting AI Features...")
        test_file = "test.py"

        result = self.code_editor.load_file(test_file)
        if not result == "File loaded successfully":
            print(f"Error: {result}")
            return

        print(f"\nLoaded test file content:\n{self.code_editor.content[:200]}...")

        print("\nTesting code analysis...")
        analysis = self.code_editor.analyze_current_code()
        print("Analysis Result:")
        print(analysis)

        print("\nTesting documentation generation...")
        self.code_editor.cursor_pos = (5, 1)
        docs = self.code_editor.get_documentation_at_cursor()
        print("Documentation Result:")
        print(docs)

        print("\nTesting code completion...")
        self.code_editor.cursor_pos = (17, 1)
        suggestions = self.code_editor.get_completion_suggestions()
        print("Completion suggestions:", suggestions)

        print("\nTesting error detection...")
        errors = self.code_editor.check_for_errors()
        if errors:
            print(f"Found {len(errors)} errors")
            for error in errors:
                print(f"Error at line {error.get('line')}: {error.get('message')}")
        else:
            print("No errors found in test file")


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ide')
def ide_route():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_code():
    try:
        code = request.json.get('code', '')
        ide.code_editor.content = code
        analysis = ide.code_editor.analyze_current_code()
        return jsonify(analysis)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/document', methods=['POST'])
def generate_documentation():
    try:
        code = request.json.get('code', '')
        position = request.json.get('position', (1, 1))
        ide.code_editor.content = code
        ide.code_editor.cursor_pos = tuple(position)
        docs = ide.code_editor.get_documentation_at_cursor()
        return jsonify(docs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/complete', methods=['POST'])
def get_completion():
    try:
        code = request.json.get('code', '')
        position = request.json.get('position', (1, 1))
        ide.code_editor.content = code
        ide.code_editor.cursor_pos = tuple(position)
        suggestions = ide.code_editor.get_completion_suggestions()
        return jsonify({"suggestions": suggestions})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate', methods=['POST'])
def generate_code():
    try:
        prompt = request.json.get('prompt', '')
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400

        response = ide.code_editor.code_assistant.client.chat.completions.create(
            model=ide.code_editor.code_assistant.model,
            messages=[
                {
                    "role": "system",
                    "content": """Generate focused Python code solutions. Follow these guidelines:
                    1. Create concise, efficient implementations
                    2. Use standard library when possible
                    3. Include brief comments for clarity
                    4. Return JSON with 'code' key containing the generated code"""
                },
                {
                    "role": "user",
                    "content": f"Create a Python script that does the following: {prompt}"
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.2,  # Lower temperature for more focused output
            max_tokens=500,   # Reduced max tokens
            top_p=0.8,        # Slightly reduced top_p
            presence_penalty=0.0  # Removed presence penalty
        )

        generated_code = response.choices[0].message.content.strip()

        try:
            result = json.loads(generated_code)
            if "code" not in result:
                raise ValueError("Response does not contain 'code' key")
            code = result["code"]
            ast.parse(code)  # Validate syntax
            return jsonify({"code": code})
        except (SyntaxError, ValueError, json.JSONDecodeError) as e:
            return jsonify({
                "error": f"Generated code is incomplete or contains errors: {str(e)}",
                "code": generated_code
            }), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/blockchain/compile', methods=['POST'])
def compile_contract():
    try:
        code = request.json.get('code', '')
        contract_name = request.json.get('name', 'Contract')

        if not code:
            return jsonify({"error": "No contract code provided"}), 400

        result = ide.contract_developer.compile_contract(code, contract_name)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/blockchain/verify', methods=['POST'])
def verify_contract():
    try:
        code = request.json.get('code', '')
        if not code:
            return jsonify({"error": "No contract code provided"}), 400

        result = ide.contract_developer.verify_contract(code)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/blockchain/estimate-gas', methods=['POST'])
def estimate_contract_gas():
    try:
        compiled_contract = request.json.get('contract')
        if not compiled_contract:
            return jsonify({"error": "No compiled contract provided"}), 400

        gas = ide.contract_developer.estimate_gas(compiled_contract)
        return jsonify({"estimated_gas": gas})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/debug/start', methods=['POST'])
def start_debugging():
    try:
        code = request.json.get('code', '')
        if not code:
            return jsonify({"error": "No code provided"}), 400

        ide.debugger.start_debugging(code)
        return jsonify({"status": "debugging_started"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/debug/stop', methods=['POST'])
def stop_debugging():
    try:
        ide.debugger.stop_debugging()
        return jsonify({"status": "debugging_stopped"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/debug/step', methods=['POST'])
def debug_step():
    try:
        step_type = request.json.get('type', 'over')
        if step_type == 'into':
            ide.debugger.step_into()
        elif step_type == 'over':
            ide.debugger.step_over()
        elif step_type == 'continue':
            ide.debugger.continue_execution()

        return jsonify({"status": "step_executed"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/debug/breakpoint', methods=['POST'])
def toggle_breakpoint():
    try:
        filename = request.json.get('filename', '')
        line = request.json.get('line', 0)

        if not filename or not line:
            return jsonify({"error": "Invalid breakpoint data"}), 400

        result = ide.debugger.toggle_breakpoint(filename, line)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/debug/state')
def get_debug_state():
    try:
        state = ide.debugger.get_debugger_state()
        output = ide.debugger.get_output()

        response = {
            "state": state,
            "output": output
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/blockchain/deploy', methods=['POST'])
def deploy_contract():
    try:
        code = request.json.get('code', '')
        contract_name = request.json.get('name', 'Contract')

        if not code:
            return jsonify({"error": "No contract code provided"}), 400

        # First compile the contract
        compiled_contract = ide.contract_developer.compile_contract(code, contract_name)

        # Then deploy it
        result = ide.contract_developer.deploy_contract(compiled_contract, contract_name)

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/docs/output/<path:filename>')
def serve_documentation(filename):
    try:
        return send_from_directory('docs/output', filename)
    except Exception as e:
        return jsonify({"error": str(e)}), 404

def main():
    global ide

    if not os.getenv("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY environment variable not set")
        print("AI-assisted features will be disabled")
        return

    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("Running in test mode...")
        ide = IDE(test_mode=True)
        ide.test_ai_features()
        return

    try:
        ide = IDE(test_mode=False)
        print("Starting IDE in web mode...")
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        print(f"\nError running IDE: {str(e)}")

if __name__ == "__main__":
    main()