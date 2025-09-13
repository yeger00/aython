# executor/server.py
import os
import tempfile
import subprocess
from jsonrpcserver import method, serve

EXECUTOR_PORT = int(os.environ.get("EXECUTOR_PORT", "5000"))

@method
def run_code(code: str) -> dict:
    # Save code to temp file
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".py") as f:
        f.write(code)
        tmp_path = f.name

    try:
        # Run python with a timeout and capture output
        proc = subprocess.run(
            ["python", tmp_path],
            capture_output=True,
            text=True,
            timeout=10
        )
        return {
            "exit_code": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr
        }
    except subprocess.TimeoutExpired:
        return {"exit_code": -1, "stdout": "", "stderr": "Execution timed out"}
    except Exception as e:
        return {"exit_code": -1, "stdout": "", "stderr": f"Execution failed: {e}"}
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass

if __name__ == "__main__":
    serve("0.0.0.0", EXECUTOR_PORT)
