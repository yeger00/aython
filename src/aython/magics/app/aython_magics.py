from datetime import datetime
import json
import os
from IPython.core.magic import Magics, line_magic, magics_class
from IPython.display import Code, display
import requests
import nbformat
from nbformat.v4 import new_notebook, new_code_cell, new_output

AGENT_URL = os.environ.get("AGENT_URL", "http://aython-agent:4000")
HEADERS = {"Content-Type": "application/json"}


class JsonRpcClient:
    """Minimal JSON-RPC client that returns only result or error message."""
    def __init__(self, url: str = AGENT_URL):
        self.url = url
        self.request_id = 1

    def call(self, method: str, params: dict = None):
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": self.request_id
        }
        self.request_id += 1
        try:
            resp = requests.post(self.url, headers=HEADERS, data=json.dumps(payload))
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            return {"error": f"Request failed: {e}"}

        if "error" in data:
            err = data["error"]
            if isinstance(err, dict):
                return {"error": err.get("message", str(err))}
            return {"error": str(err)}

        return data.get("result", {})


client = JsonRpcClient()


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
            res = client.call("init_agent", {"model": model})
            if "error" in res:
                print("❌", res["error"])
            else:
                print(res.get("message"))
        except Exception as e:
            print("Failed to init agent:", e)

    @line_magic
    def code(self, line):
        """Request agent to generate code and run it."""
        if not line.strip():
            print("Usage: %code <requirements>")
            return

        try:
            res = client.call("generate_and_run", {"requirements": line.strip()})
        except Exception as e:
            print("Agent call failed:", e)
            return

        debug = None
        if "error" in res:
            print("❌", res["error"])
            debug = res.get("debug_log")
        if debug:
            print("📝 debug_log:\n", debug)
            return

        code_text = res.get("code_snippet", "")
        execution = res.get("execution_result", {})

        if code_text:
            # Display the generated code
            display(Code(code_text, language="python"))
            
            # Execute the code directly in the notebook
            print("🚀 Executing generated code in notebook...")
            try:
                # Execute the code in the current namespace
                exec(code_text, self.shell.user_ns)
                print("✅ Code executed successfully!")
            except Exception as e:
                print(f"❌ Error executing code: {e}")
                # Also show the agent's execution results for comparison
                stdout = execution.get("stdout") or ""
                stderr = execution.get("stderr") or ""
                if stdout:
                    print(f"Agent execution stdout: {stdout}")
                if stderr:
                    print(f"Agent execution stderr: {stderr}")
        else:
            print("❌ No code generated")

        # Save to Out cache
        out_entry = {
            "generated code": code_text,
            "execution_result": "executed_in_notebook",
            "display": []
        }
        self.shell.user_ns.setdefault("Out", {})
        self.shell.user_ns["Out"][self.shell.execution_count] = out_entry

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
