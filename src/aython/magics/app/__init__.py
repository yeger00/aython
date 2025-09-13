from .aython_magics import AythonMagics

def load_ipython_extension(ipython):
    ipython.register_magics(AythonMagics)