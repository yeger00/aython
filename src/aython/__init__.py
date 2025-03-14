__version__ = "0.1.0"
__all__ = ["aython"]

import multiprocessing as mp
from dataclasses import dataclass
from typing import Optional
from textual.app import App
from textual.widgets import Input, ListView, Static
from textual.containers import Container
from textual.reactive import reactive
from textual.binding import Binding

@dataclass
class CommandResult:
    """Result of a command execution"""
    output: str
    error: Optional[str] = None
    exit_code: int = 0

def python_process_worker(input_queue: mp.Queue, output_queue: mp.Queue):
    """Worker function that runs in separate process to execute Python commands"""
    import sys
    import io
    from contextlib import redirect_stdout, redirect_stderr

    while True:
        command = input_queue.get()
        if command == "EXIT":
            break
            
        # Capture stdout and stderr
        stdout = io.StringIO()
        stderr = io.StringIO()
        exit_code = 0
        
        try:
            with redirect_stdout(stdout), redirect_stderr(stderr):
                exec(command)
        except Exception as e:
            stderr.write(str(e))
            exit_code = 1
            
        result = CommandResult(
            output=stdout.getvalue(),
            error=stderr.getvalue() if stderr.getvalue() else None,
            exit_code=exit_code
        )
        output_queue.put(result)

class PythonCommandPalette(App):
    """A Warp-like command palette focused on Python operations."""
    
    # Reactive variable to store command output
    command_output = reactive("")
    
    CSS = """
    Screen {
        background: #1C1E26;
    }

    Input {
        dock: bottom;
        margin: 1 2;
        padding: 1 2;
        background: #2E303E;
        color: #FFFFFF;
        border: none;
        height: 3;
    }
    
    #output {
        height: 1fr;
        background: #1C1E26;
        color: #FFFFFF;
        padding: 1 2;
        border: solid #2E303E;
        border-bottom: none;
    }
    
    ListView {
        height: 1fr;
        background: #1C1E26;
        color: #FFFFFF;
        border: solid #2E303E;
    }

    ListView > ListItem {
        padding: 1 2;
    }

    ListView > ListItem:hover {
        background: #2E303E;
    }

    ListView > ListItem.--highlight {
        background: #2E303E;
    }

    .error {
        color: #FF6E6E;
    }

    .success {
        color: #95E6CB;
    }
    """

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", show=False),
        Binding("ctrl+k", "clear", "Clear", show=False),
    ]

    def __init__(self):
        super().__init__()
        # Create communication queues
        self.input_queue = mp.Queue()
        self.output_queue = mp.Queue()
        
        # Create and start the worker process
        self.worker = mp.Process(
            target=python_process_worker,
            args=(self.input_queue, self.output_queue)
        )
        self.worker.start()

    def compose(self):
        """Create child widgets for the app."""
        yield Container(
            Static(id="output"),
            ListView(id="suggestions"),
            Input(placeholder="Enter Python command...", id="command_input")
        )

    def on_mount(self):
        """Handle app startup."""
        self.query_one(Input).focus()
        # Start checking for command output
        self.set_interval(1/60, self.check_command_output)

    def check_command_output(self):
        """Check for any output from the worker process"""
        try:
            while not self.output_queue.empty():
                result = self.output_queue.get_nowait()
                output = result.output
                if result.error:
                    output += f"\nError: {result.error}"
                self.command_output = output
        except Exception as e:
            self.command_output = f"Error checking output: {str(e)}"

    def watch_command_output(self, output: str):
        """React to changes in command output"""
        output_widget = self.query_one("#output")
        if output.strip():
            if "Error:" in output:
                output_widget.set_classes("error")
            else:
                output_widget.set_classes("success")
        output_widget.update(output)

    async def on_input_submitted(self, message: Input.Submitted):
        """Handle command input"""
        command = message.value
        # Clear the input
        message.input.value = ""
        
        # Send command to worker process
        self.input_queue.put(command)

    def on_unmount(self):
        """Clean up when the app exits"""
        # Tell the worker to exit
        self.input_queue.put("EXIT")
        # Wait for the worker to finish
        self.worker.join(timeout=1)
        # Force terminate if it didn't exit cleanly
        if self.worker.is_alive():
            self.worker.terminate()

    def action_clear(self):
        """Clear the output screen"""
        self.command_output = ""

def run():
    app = PythonCommandPalette()
    app.run()

if __name__ == "__main__":
    print("Starting Aython...")
    run()