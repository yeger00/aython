from datetime import datetime
import json
import os
from IPython.core.magic import Magics, line_magic, magics_class
from IPython.display import Code, display
import requests
import json
import nbformat
from nbformat.v4 import new_notebook, new_code_cell, new_output

AGENT_URL = os.environ.get("AGENT_URL", "http://aython-agent:4000")
headers = {"Content-Type": "application/json"}
@magics_class
class AythonMagics(Magics):
    def __init__(self, shell):
        super().__init__(shell)

    @line_magic
    def init_aython(self, line):
        model = line.strip()
        if not model:
            print("Usage: %init_aython <model>")
            return
        try:
            payload = {
            "jsonrpc": "2.0",
            "method": "init_agent",
            "params": {"model": model},
            "id": 1
            }
            response = requests.post(AGENT_URL, headers=headers, data=json.dumps(payload))
            
            print(response.json())
        except Exception as e:
            print("Failed to init agent:", e)

    @line_magic
    def code(self, line):
        """Request agent to generate code and run it."""
        if not line.strip():
            print("Usage: %code <requirements>")
            return
        try:
            payload = {
                "jsonrpc": "2.0",
                "method": "generate_and_run",
                "params": {"requirements": line.strip()},
                "id": 2
            }
            response = requests.post(AGENT_URL, headers=headers, data=json.dumps(payload))
            
        except Exception as e:
            print("Agent call failed:", e)
            return

        result = response.json()
        if "error" in result:
            print("❌", result["error"])
            return

        code_text = result.get("code_snippet", "")  # your agent returns `code_snippet`
        execution = result.get("execution", {})

        display(Code(code_text, language="python"))

        out_entry = {
            "generated code": code_text,
            "exit_code": execution.get("exit_code"),
            "stdout": execution.get("stdout"),
            "stderr": execution.get("stderr"),
            "display": []
        }

        self.shell.user_ns.setdefault("Out", {})
        self.shell.user_ns["_"] = execution.get("stdout")
        self.shell.user_ns["Out"][self.shell.execution_count] = out_entry

        stdout = execution.get("stdout") or ""
        stderr = execution.get("stderr") or ""
        if stdout:
            print(stdout, end="")
        if stderr:
            print("⚠️ stderr:\n", stderr)

    @line_magic
    def save_history(self, line):
        filename = line.strip() or f"ipython_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        ip = self.shell
        out_cache = ip.user_ns.get("Out", {})

        history = []
        for session_id, line_num, cell in ip.history_manager.get_range(raw=True):
            if not cell.strip() or cell.strip().startswith(("%save_history", "%export_notebook")):
                continue
            entry = {"session": session_id, "line": line_num, "input": cell}
            if line_num in out_cache:
                entry["output"] = out_cache[line_num]
            history.append(entry)

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)

        print(f"✅ History saved to {os.path.abspath(filename)}")

    @line_magic
    def export_notebook(self, line):
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
                if entry.get("stdout"):
                    outputs.append(new_output(output_type="stream", name="stdout", text=entry["stdout"]))
                if entry.get("stderr"):
                    outputs.append(new_output(output_type="stream", name="stderr", text=entry["stderr"]))
                if entry.get("display"):
                    for d in entry["display"]:
                        outputs.append(new_output(output_type="display_data",
                                                  data={"text/plain": str(d)}, metadata={}))
                if entry.get("result") and not outputs:
                    outputs.append(new_output(output_type="execute_result",
                                              data={"text/plain": str(entry["result"])},
                                              metadata={},
                                              execution_count=line_num))

            code_cell["outputs"] = outputs
            code_cell["execution_count"] = line_num
            nb.cells.append(code_cell)

        with open(filename, "w", encoding="utf-8") as f:
            nbformat.write(nb, f)

        print(f"✅ Notebook exported to {os.path.abspath(filename)}")

def load_ipython_extension(ipython):
    ipython.register_magics(AythonMagics)
