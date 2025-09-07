from functools import partial
import json

from textwrap import dedent
from typing import Any
from pydantic import BaseModel
from agno.agent import Agent, RunResponse
from agno.models.openai import OpenAIChat
from agno.models.google import Gemini
from agno.storage.agent.sqlite import SqliteAgentStorage
from agno.tools.reasoning import ReasoningTools

from python_runner import build_python_docker, run_python_docker

def check_code(code_snippet: str) -> bool:
    try:
        compile(code_snippet, '<string>', 'exec')
    except SyntaxError as e:
        return False
    return True

class CodeResult(BaseModel):
    """A model to hold the generated code snippet."""
    name: str
    code_snippet: str
    deps: list[str]
    # TODO: add config
    # config: Any


class AythonAgent():
    def __init__(self, model_str: str, debug: bool = False):
        if "gemini" in model_str.lower():
            model = Gemini(id=model_str)
        elif "gpt" in model_str.lower():
            model = OpenAIChat(id=model_str)
        else:
            raise ValueError(f"Error: Unsupported model name '{model_str}'. Please choose a Gemini or GPT model.")
        self.debug = debug
        self.agent = Agent(
            name="MCP GitHub Agent",
            instructions=dedent("""
                You are a Python coding agent know how to write python code.
            """),
            model=model,
            storage=SqliteAgentStorage(
                table_name="basic_agent",
                auto_upgrade_schema=True,
            ),
            add_history_to_messages=True,
            num_history_responses=3,
            add_datetime_to_instructions=True,
            markdown=True,
            response_model=CodeResult,
        )

        self.retries = 3

    def code(self, user_requirements: str, current_context: str = "") -> CodeResult:
        try:
            i = 0
            while i < self.retries:
                instructions = f"""
You are a Python expert, that will help create a Python script for the user.
The code you return will run inside a continaer from "python:3.11-slim".
Every dependnecy the script is require to run, you should put in `deps`. 
If there are no dependnecies, `deps` should be an empty list `[]`.
The script itself should be in `code_snippet`.
Decide on a `name`, use snake_case.

user requirements: {user_requirements}.
                """
                if self.debug:
                    print(instructions)
                response: RunResponse = self.agent.run(
                    instructions,
                    stream=False,
                    show_full_reasoning=True,
                    stream_intermediate_steps=True,
                )
                i += 1
                generated_code = response.content.code_snippet
                image_name = response.content.name
                # TODO: after adding memory, just send the error instead of randomly re-generate
                if not check_code(generated_code):
                    print("failed to compile code, retring")
                    continue
                
                build_python_docker(generated_code, response.content.deps, image_name)
                return partial(run_python_docker, image_name)
                
            # Failed to generate code
        except Exception as e:
            print(f"Error during code generation: {e}")