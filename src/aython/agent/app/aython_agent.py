# agent/app/aython_agent.py
import json
from textwrap import dedent
from pydantic import BaseModel
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.google import Gemini
from agno.tools.reasoning import ReasoningTools


def check_code(code_snippet: str) -> bool:
    """Check if a code snippet is valid Python."""
    try:
        compile(code_snippet, '<string>', 'exec')
    except SyntaxError:
        return False
    return True


class CodeResult(BaseModel):
    """A model to hold the generated code snippet."""
    code_snippet: str


class AythonAgent:
    def __init__(self, model_str: str, debug: bool = False):
        if "gemini" in model_str.lower():
            if not model_str.startswith("models/"):
                model_str = f"models/{model_str}"
            model = Gemini(id=model_str)
        elif "gpt" in model_str.lower():
            model = OpenAIChat(id=model_str)
        else:
            raise ValueError(
                f"Unsupported model name '{model_str}'. Use Gemini or GPT."
            )

        self.debug = debug

        # New Agent init for agno>=1.8, no storage argument
        self.agent = Agent(
            name="MCP GitHub Agent",
            instructions=dedent("""
                You are a Python coding agent. You know how to write Python code.
            """),
            model=model,
            tools=[ReasoningTools()],
           
        )
        self.retries = 3

    def code(self, user_requirements: str, current_context: str = "") -> CodeResult:
        """Generate Python code based on user requirements."""
        try:
            for _ in range(self.retries):
                instructions = f"""
                Create a Python function that does the following: {user_requirements}.
                Return ONLY valid JSON in this format:
                {{
                  "code_snippet": "<your python code here>"
                }}
                """
                if self.debug:
                    print("Instructions sent to agent:\n", instructions)

                response = self.agent.run(
                    instructions,
                    stream=False,
                    show_full_reasoning=True,
                    stream_intermediate_steps=True,
                )

                # Handle response content
                try:
                    generated_code = response.content.code_snippet
                except AttributeError:
                    print("Failed to parse model response into CodeResult.")
                    generated_code = str(response.content) if response.content else ""

                if check_code(generated_code):
                    return CodeResult(code_snippet=generated_code)

            return CodeResult(code_snippet="")  # signal failure

        except Exception as e:
            print(f"Error during code generation: {e}")
            return CodeResult(code_snippet="")
