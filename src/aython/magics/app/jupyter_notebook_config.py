# Jupyter configuration to automatically load Aython magics
c = get_config()

# Auto-load the Aython magics extension
c.InteractiveShellApp.extensions = [
    'aython_magics'
]

# Set up the magics to be available in all notebooks
c.InteractiveShellApp.exec_lines = [
    'import sys',
    'sys.path.insert(0, "/app")',
    'from aython_magics import AythonMagics',
    'ip = get_ipython()',
    'ip.register_magics(AythonMagics)',
    'print("✅ Aython magics loaded! Use %init_aython and %code commands.")'
]
