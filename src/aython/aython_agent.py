import json

import litellm
from pydantic import BaseModel


class StaticAnalysis:
    def check(self, code_snippet):
        pass

    def fix(self, code_snippet):
        pass

# TODO: understand if this is possible?
class DynamicAnalysis:
    def check(self, code_snippet):
        pass

    def fix(self, code_snippet):
        pass


class CodeResult(BaseModel):
    """A model to hold the generated code snippet."""
    code_snippet: str


class AythonAgent():
    def __init__(self, model: str):
        self.model = model

    def code(self, user_requirements: str) -> CodeResult:
        """Generate and load code into the IPython scope."""
        messages = [
            {
                "role": "user",
                "content": f"Create a Python function that does the following: {user_requirements}.",
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
            # TODO: use static and dynamic analysis in order to verify the code
            # TODO: if the validation fail, use the llm again up to 3 tries.
            return generated_code
        except Exception as e:
            print(f"Error during code generation: {e}")