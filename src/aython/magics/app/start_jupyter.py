# magics/app/start_jupyter.py
import os
import sys

print("Starting Jupyter Lab with Aython magics...")
os.environ.setdefault("JUPYTER_TOKEN", "")

# Add the current directory to Python path so magics can be imported
sys.path.insert(0, '/app')

cmd = [
    "jupyter", "lab",
    "--ip=0.0.0.0",
    "--no-browser",
    "--allow-root",
    "--NotebookApp.token=",
    "--NotebookApp.password=",
    "--ServerApp.token=",
    "--ServerApp.password="
]
os.execvp("jupyter", cmd)
