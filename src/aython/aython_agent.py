import json

from textwrap import dedent
from pydantic import BaseModel
from agno.agent import Agent, RunResponse
from agno.models.openai import OpenAIChat
from agno.models.google import Gemini
from agno.storage.agent.sqlite import SqliteAgentStorage
from agno.tools.reasoning import ReasoningTools

def check_code(code_snippet: str) -> bool:
    try:
        compile(code_snippet, '<string>', 'exec')
    except SyntaxError as e:
        return False
    return True

class CodeResult(BaseModel):
    """A model to hold the generated code snippet."""
    code_snippet: str


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
Create a Python function that does the following: {user_requirements}.
                """
                if self.debug:
                    print(instructions)
                response: RunResponse = self.agent.run(
                    instructions,
                    stream=False,
                    show_full_reasoning=True,
                    stream_intermediate_steps=True,
                )
                generated_code = response.content.code_snippet
                # TODO: after adding memory, just send the error instead of randomly re-generate
                if check_code(generated_code):
                    return generated_code
                i += 1
            # Failed to generate code
        except Exception as e:
            print(f"Error during code generation: {e}")