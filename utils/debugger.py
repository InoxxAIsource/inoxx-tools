"""Real-time Python code debugger module."""
import sys
import bdb
import threading
from typing import Dict, List, Any, Optional
from queue import Queue

class InoxxDebugger(bdb.Bdb):
    """Custom debugger implementation for Inoxx IDE."""
    def __init__(self):
        super().__init__()
        self.breakpoints: Dict[str, List[int]] = {}
        self.current_frame = None
        self.is_running = False
        self.step_command = None
        self.command_queue = Queue()
        self.output_queue = Queue()
        self.variables: Dict[str, Any] = {}
        self.call_stack: List[Dict[str, Any]] = []

    def start(self, code: str) -> None:
        """Start debugging session."""
        self.is_running = True
        try:
            # Execute code in debug mode
            self.run(code)
        except Exception as e:
            self.output_queue.put({
                "type": "error",
                "message": str(e)
            })
        finally:
            self.is_running = False

    def set_break(self, filename: str, lineno: int, temporary: bool = False, 
                  cond: str = None, funcname: str = None) -> None:
        """Set a breakpoint."""
        super().set_break(filename, lineno, temporary, cond, funcname)
        if filename not in self.breakpoints:
            self.breakpoints[filename] = []
        self.breakpoints[filename].append(lineno)

    def clear_break(self, filename: str, lineno: int) -> None:
        """Clear a breakpoint."""
        super().clear_break(filename, lineno)
        if filename in self.breakpoints:
            self.breakpoints[filename].remove(lineno)

    def clear_all_breaks(self) -> None:
        """Clear all breakpoints."""
        super().clear_all_breaks()
        self.breakpoints.clear()

    def user_line(self, frame) -> None:
        """Called when debugger reaches a new line."""
        self.current_frame = frame
        self._update_state()

        # Send immediate state update
        self.output_queue.put({
            "type": "state_update",
            "position": {
                "file": frame.f_code.co_filename,
                "line": frame.f_lineno
            },
            "variables": self._get_variables(),
            "call_stack": self._get_call_stack()
        })

        # Wait for next command
        command = self.command_queue.get()
        if command:
            self.step_command = command

    def _get_variables(self) -> Dict[str, Any]:
        """Get current variables in scope."""
        if not self.current_frame:
            return {}

        # Get local and global variables with proper filtering
        locals_dict = {}
        for key, value in self.current_frame.f_locals.items():
            try:
                # Convert values to string representation safely
                locals_dict[key] = repr(value)
            except Exception:
                locals_dict[key] = "<unprintable value>"

        globals_dict = {}
        for key, value in self.current_frame.f_globals.items():
            if key.startswith('__'):
                continue
            try:
                globals_dict[key] = repr(value)
            except Exception:
                globals_dict[key] = "<unprintable value>"

        return {
            "locals": locals_dict,
            "globals": globals_dict
        }

    def _get_call_stack(self) -> List[Dict[str, Any]]:
        """Get current call stack with detailed information."""
        if not self.current_frame:
            return []

        stack = []
        frame = self.current_frame
        while frame:
            stack.append({
                "filename": frame.f_code.co_filename,
                "function": frame.f_code.co_name,
                "lineno": frame.f_lineno,
                "locals": {
                    key: repr(value) 
                    for key, value in frame.f_locals.items()
                    if not key.startswith('__')
                }
            })
            frame = frame.f_back
        return stack

    def _update_state(self) -> None:
        """Update debugger state information."""
        if not self.current_frame:
            return

        self.variables = self._get_variables()
        self.call_stack = self._get_call_stack()

    def get_current_state(self) -> Dict[str, Any]:
        """Get current debugger state."""
        return {
            "is_running": self.is_running,
            "breakpoints": self.breakpoints,
            "variables": self.variables,
            "call_stack": self.call_stack
        }

class DebuggerController:
    """Controller class for managing debugging sessions."""
    def __init__(self):
        self.debugger = InoxxDebugger()
        self.debug_thread: Optional[threading.Thread] = None

    def start_debugging(self, code: str) -> None:
        """Start a new debugging session."""
        if self.debug_thread and self.debug_thread.is_alive():
            return

        self.debug_thread = threading.Thread(
            target=self.debugger.start,
            args=(code,)
        )
        self.debug_thread.start()

    def stop_debugging(self) -> None:
        """Stop current debugging session."""
        if self.debug_thread and self.debug_thread.is_alive():
            self.debugger.command_queue.put(None)
            self.debug_thread.join()

    def step_over(self) -> None:
        """Execute next line, stepping over function calls."""
        self.debugger.command_queue.put("next")

    def step_into(self) -> None:
        """Execute next line, stepping into function calls."""
        self.debugger.command_queue.put("step")

    def continue_execution(self) -> None:
        """Continue execution until next breakpoint."""
        self.debugger.command_queue.put("continue")

    def toggle_breakpoint(self, filename: str, line: int) -> Dict[str, Any]:
        """Toggle breakpoint at specified line."""
        if filename in self.debugger.breakpoints and line in self.debugger.breakpoints[filename]:
            self.debugger.clear_break(filename, line)
            return {"action": "removed", "line": line}
        else:
            self.debugger.set_break(filename, line)
            return {"action": "added", "line": line}

    def get_debugger_state(self) -> Dict[str, Any]:
        """Get current debugger state."""
        return self.debugger.get_current_state()

    def get_output(self) -> Optional[Dict[str, Any]]:
        """Get next output message from debugger."""
        try:
            return self.debugger.output_queue.get_nowait()
        except:
            return None