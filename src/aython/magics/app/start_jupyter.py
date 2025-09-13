# magics/app/start_jupyter.py
import os

print("Starting Jupyter Lab...")
os.environ.setdefault("JUPYTER_TOKEN", "")

cmd = [
    "jupyter", "lab",
    "--ip=0.0.0.0",
    "--no-browser",
    "--allow-root",
    "--NotebookApp.token=",
    "--NotebookApp.password="
]
os.execvp("jupyter", cmd)
