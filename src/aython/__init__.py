from IPython.core.magic import Magics, line_magic, magics_class
from IPython.display import Code, display
from aython.aython_agent import AythonAgent


@magics_class
class AythonMagics(Magics):
    def __init__(self, shell):
        super().__init__(shell)
        self.aython = None

    @line_magic
    def init_aython(self, line):
        """Set the model to use for code generation."""
        if self.aython:
            print("Aython is already initialized")
        self.aython = AythonAgent(line.strip())

    @line_magic
    def code(self, line):
        if not self.aython:
            print("Please init aython first using %init_aython <model_name>")
            return

        """Generate and load a function into the IPython scope."""
        generated_code = self.aython.code(line)
        if not generated_code:
            return
        display(Code(generated_code, language="python"))
        self.shell.run_cell(generated_code)


def load_ipython_extension(ipython):
    """Load the extension in IPython."""
    ipython.register_magics(AythonMagics)