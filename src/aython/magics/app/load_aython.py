# Load Aython magics into the current IPython session
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, '/app')

try:
    from aython_magics import AythonMagics
    from IPython import get_ipython
    
    # Get the current IPython instance
    ip = get_ipython()
    if ip is not None:
        # Register the magics
        ip.register_magics(AythonMagics)
        print("✅ Aython magics loaded successfully!")
        print("Available commands:")
        print("  %init_aython <model>  - Initialize the AI agent")
        print("  %code <requirements>  - Generate and execute code")
        print("  %save_history <file>  - Save session history")
        print("  %export_notebook <file> - Export as Jupyter notebook")
    else:
        print("❌ No IPython session found. Please run this in a Jupyter notebook.")
except ImportError as e:
    print(f"❌ Failed to import Aython magics: {e}")
except Exception as e:
    print(f"❌ Error loading Aython magics: {e}")
