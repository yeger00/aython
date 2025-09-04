import json

import litellm
from IPython.core.magic import Magics, line_magic, magics_class
from IPython.display import Code, display
from pydantic import BaseModel


class CodeResult(BaseModel):
    """A model to hold the generated code snippet."""

    code_snippet: str


@magics_class
class AythonMagics(Magics):
    def __init__(self, shell):
        super().__init__(shell)
        self.model = None

    @line_magic
    def set_model(self, line):
        """Set the model to use for code generation."""
        self.model = line.strip()
        print(f"Model set to: {self.model}")

    @line_magic
    def code(self, line):
        """Generate and load a function into the IPython scope."""
        if not self.model:
            print("Please set a model first using %set_model <model_name>")
            return

        messages = [
            {
                "role": "user",
                "content": f"Create a Python function that does the following: {line}.",
            }
        ]
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "code_result",
                    "description": "A function to hold the generated code snippet.",
                    "parameters": CodeResult.model_json_schema(),
                },
            }
        ]

        try:
            response = litellm.completion(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice={"type": "function", "function": {"name": "code_result"}},
            )
            tool_call = response.choices[0].message.tool_calls[0]
            arguments = json.loads(tool_call.function.arguments)
            generated_code = CodeResult(**arguments).code_snippet

            display(Code(generated_code, language="python"))
            self.shell.run_cell(generated_code)
        except Exception as e:
            print(f"Error during code generation: {e}")


def load_ipython_extension(ipython):
    """Load the extension in IPython."""
    ipython.register_magics(AythonMagics)