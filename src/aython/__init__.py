from datetime import datetime
import json
import os
from IPython.core.magic import Magics, line_magic, magics_class
from IPython.display import Code, display
from IPython.utils.capture import capture_output
from aython.aython_agent import AythonAgent
import nbformat
from nbformat.v4 import new_notebook, new_code_cell, new_output

@magics_class
class AythonMagics(Magics):
    def __init__(self, shell):
        super().__init__(shell)
        self.aython = None

    @line_magic
    def init_aython(self, line):
        """Initialize the Aython agent with a model."""
        if self.aython:
            print("Aython is already initialized")
            return
        self.aython = AythonAgent(line.strip())
        print(f"✅ Aython initialized with model: {line.strip()}")

    @line_magic
    def code(self, line):
        """Generate Python code from Aython, run it, and capture outputs."""
        if not self.aython:
            print("Please init aython first using %init_aython <model_name>")
            return

        # Generate code
        result = self.aython.code(line)
        if not result or not result.code_snippet:
            print("❌ No code generated.")
            return

        code_text = result.code_snippet
        display(Code(code_text, language="python"))
          # Prepare Out entry
       
        
        out_entry = {
            "generated code": code_text,  # Correctly capture stdout
        }
        self.shell.user_ns["Out"][self.shell.execution_count] = out_entry
        # Capture stdout, stderr, and display objects
        with capture_output() as captured:
            exec_result = self.shell.run_cell(code_text)
            if exec_result is not None or exec_result != "":
                    
                # Prepare Out entry
                out_entry.update({
                    "result": exec_result.result,
                    "stdout": captured.stdout,
                    "stderr": captured.stderr,
                    "display": [repr(o) for o in captured.outputs]
                })

                # Save to Out manually
                if "Out" not in self.shell.user_ns:
                    self.shell.user_ns["Out"] = {}
                # This will save the result of the last executed cell
                self.shell.user_ns["_"] = exec_result.result
                # The key for the Out dictionary should be the execution count of the *current* cell
        
        self.shell.user_ns["Out"][self.shell.execution_count] = out_entry

    @line_magic
    def save_history(self, line):
        """Save IPython command history including inputs, stdout, stderr, display, and return value."""
        filename = line.strip() or f"ipython_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        ip = self.shell
        out_cache = ip.user_ns.get("Out", {})

        history = []
        for session_id, line_num, cell in ip.history_manager.get_range(raw=True):
            if not cell.strip() or cell.strip().startswith(("%save_history", "%export_notebook")):
                continue
            entry = {
                "session": session_id,
                "line": line_num,
                "input": cell
            }
            if line_num in out_cache:
                entry["output"] = out_cache[line_num]
            history.append(entry)

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)

        print(f"✅ History with outputs saved to {os.path.abspath(filename)}")

    @line_magic
    def export_notebook(self, line):
        """Export current IPython history to a .ipynb notebook."""
        filename = line.strip() or f"ipython_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ipynb"
        ip = self.shell
        out_cache = ip.user_ns.get("Out", {})

        nb = new_notebook()
        for session_id, line_num, cell in ip.history_manager.get_range(raw=True):
            if not cell.strip() or cell.strip().startswith(("%save_history", "%export_notebook")):
                continue

            code_cell = new_code_cell(source=cell)
            outputs = []

            if line_num in out_cache:
                entry = out_cache[line_num]
                # stdout
                if entry.get("stdout"):
                    outputs.append(new_output(output_type="stream", name="stdout", text=entry["stdout"]))
                # stderr
                if entry.get("stderr"):
                    outputs.append(new_output(output_type="stream", name="stderr", text=entry["stderr"]))
                # display
                if entry.get("display"):
                    for d in entry["display"]:
                        outputs.append(new_output(output_type="display_data",
                                                  data={"text/plain": str(d)}, metadata={}))
                # result (if nothing else captured)
                if entry.get("result") and not outputs:
                    outputs.append(new_output(output_type="execute_result",
                                              data={"text/plain": str(entry["result"])},
                                              metadata={},
                                              execution_count=line_num))

            code_cell["outputs"] = outputs
            code_cell["execution_count"] = line_num
            nb.cells.append(code_cell)

        # Save notebook
        with open(filename, "w", encoding="utf-8") as f:
            nbformat.write(nb, f)

        print(f"✅ Notebook exported to {os.path.abspath(filename)}")


def load_ipython_extension(ipython):
    """Load the extension in IPython."""
    ipython.register_magics(AythonMagics)
