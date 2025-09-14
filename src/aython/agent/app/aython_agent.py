# agent/app/aython_agent.py
import json
import re
import os
import tempfile
import subprocess
from textwrap import dedent
from pydantic import BaseModel
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.google import Gemini
from agno.tools.reasoning import ReasoningTools


def _strip_fences(text: str) -> str:
    """Remove markdown fences like ```python ... ``` from text."""
    if not text:
        return ""
    # remove opening fence with optional language
    text = re.sub(r"\s*```[a-zA-Z]*\n?", "", text)
    # remove closing or stray ```
    text = re.sub(r"\s*```", "", text)
    return text.strip()


def check_code(code_snippet: str) -> bool:
    """Check if a code snippet is valid Python."""
    cleaned = _strip_fences(code_snippet)
    try:
        compile(cleaned, "<string>", "exec")
    except SyntaxError as e:
        print("❌ SyntaxError in generated code:", e)
        print("Code was:\n", cleaned)
        return False
    return True


def clean_model_output(raw: str) -> str:
    """Remove markdown fences and extract JSON or code snippet."""
    if not raw:
        return ""

    text = raw.strip()
    text = _strip_fences(text)

    # try to parse JSON first
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict) and "code_snippet" in parsed:
            return _strip_fences(parsed["code_snippet"])
    except Exception:
        pass

    return text


class CodeResult(BaseModel):
    """A model to hold the generated code snippet."""
    code_snippet: str
    debug_log: str = ""


class ExecutionResult(BaseModel):
    """A model to hold execution results."""
    exit_code: int
    stdout: str
    stderr: str


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
        logs = []

        try:
            for attempt in range(1, self.retries + 1):
                instructions = f"""
                Create a Python function that does the following: {user_requirements}.
                Return ONLY valid JSON in this format without any extra text, comments, or explanation:
                {{
                  "code_snippet": "<your python code here>"
                }}
                """

                logs.append(f"[Attempt {attempt}] Instructions:\n{instructions}")

                try:
                    response = self.agent.run(
                        instructions,
                        stream=False,
                        show_full_reasoning=True,
                        stream_intermediate_steps=True,
                    )
                    logs.append(f"[Attempt {attempt}] Raw response: {repr(response.content)}")
                except Exception as e:
                    logs.append(f"[Attempt {attempt}] Agent.run() raised: {e}")
                    continue

                # Try extracting code
                raw_output = getattr(response.content, "code_snippet", None)
                if not raw_output:
                    raw_output = str(response.content) if response.content else ""
                cleaned = clean_model_output(raw_output)

                logs.append(f"[Attempt {attempt}] Cleaned code:\n{cleaned}")

                if cleaned and check_code(cleaned):
                    logs.append(f"[Attempt {attempt}] check_code passed")
                    return CodeResult(code_snippet=_strip_fences(cleaned), debug_log="\n".join(logs))
                else:
                    logs.append(f"[Attempt {attempt}] check_code failed")

            logs.append("All retries exhausted → returning empty code snippet.")
            return CodeResult(code_snippet="", debug_log="\n".join(logs))

        except Exception as e:
            logs.append(f"Unexpected error during code generation: {e}")
            return CodeResult(code_snippet="", debug_log="\n".join(logs))

    def execute_code(self, code: str, timeout: int = 10) -> ExecutionResult:
        """Execute Python code and return the results."""
        # Save code to temp file
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".py") as f:
            f.write(code)
            tmp_path = f.name

        try:
            # Run python with a timeout and capture output
            proc = subprocess.run(
                ["python", tmp_path],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return ExecutionResult(
                exit_code=proc.returncode,
                stdout=proc.stdout,
                stderr=proc.stderr
            )
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr="Execution timed out"
            )
        except Exception as e:
            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution failed: {e}"
            )
        finally:
            try:
                os.remove(tmp_path)
            except Exception:
                pass

    def generate_and_execute(self, user_requirements: str, current_context: str = "") -> dict:
        """Generate Python code and execute it, returning both code and execution results."""
        # Generate code
        code_result = self.code(user_requirements, current_context)
        
        if not code_result.code_snippet.strip():
            return {
                "code_snippet": "",
                "execution_result": None,
                "debug_log": code_result.debug_log,
                "error": "No code generated"
            }
        
        # Execute the code
        execution_result = self.execute_code(code_result.code_snippet)
        
        return {
            "code_snippet": code_result.code_snippet,
            "execution_result": execution_result,
            "debug_log": code_result.debug_log,
            "error": None
        }
