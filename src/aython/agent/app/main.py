# agent/app/main.py
import os
from jsonrpcserver import method, serve, Success, Error
from aython_agent import AythonAgent

AGENT_PORT = int(os.environ.get("AGENT_PORT", "4000"))
_default_model = os.environ.get("MODEL", "gpt-4o-mini")

_agent = None

@method
def init_agent(model: str = None):
    global _agent
    m = model or _default_model
    try:
        _agent = AythonAgent(m)
        return Success({"message": f"Aython initialized with model {m}"})
    except Exception as e:
        return Error(code=-32000, message=str(e))

@method
def generate_and_run(requirements: str):
    global _agent
    if not _agent:
        return Error(code=-32001, message="Agent not initialized")

    result = _agent.code(requirements)
    if not result or not result.code_snippet.strip():
        return Error(code=-32002, message="No code generated")

    try:
        exec(result.code_snippet, globals())
        return Success({"code_snippet": result.code_snippet})
    except Exception as e:
        return Error(code=-32003, message=str(e), data={"code_snippet": result.code_snippet})

if __name__ == "__main__":
    serve("0.0.0.0", AGENT_PORT)
