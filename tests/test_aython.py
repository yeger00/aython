import json
from unittest.mock import MagicMock, patch

import pytest
from IPython.testing.globalipapp import get_ipython

from aython import AythonMagics, load_ipython_extension


@pytest.fixture
def ip():
    """Fixture for a clean IPython instance."""
    ip = get_ipython()
    # Re-register the magics for each test
    load_ipython_extension(ip)
    return ip


def test_load_ipython_extension(ip):
    """Test that the extension loads and registers the magics."""
    assert "aython" in ip.magics_manager.magics
    assert isinstance(ip.magics_manager.magics["line"]["set_model"].__self__, AythonMagics)
    assert isinstance(ip.magics_manager.magics["line"]["code"].__self__, AythonMagics)


def test_set_model_magic(ip):
    """Test the %set_model magic command."""
    ip.run_line_magic("set_model", "my-model")
    magics = ip.magics_manager.magics["line"]["set_model"].__self__
    assert magics.model == "my-model"


def test_code_magic_no_model(ip):
    """Test the %code magic command without a model set."""
    result = ip.run_line_magic("code", "create a function")
    # This is a placeholder; in a real scenario, you'd capture stdout
    # and assert the error message is present.
    assert result is None


@patch("litellm.completion")
def test_code_magic_with_model(mock_completion, ip):
    """Test the %code magic command with a model set."""
    # Mock the litellm.completion function to return a tool call
    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_message = MagicMock()
    mock_tool_call = MagicMock()
    mock_function = MagicMock()

    mock_function.arguments = json.dumps({"code_snippet": "def my_generated_function():\n    pass"})
    mock_tool_call.function = mock_function
    mock_message.tool_calls = [mock_tool_call]
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    mock_completion.return_value = mock_response

    ip.run_line_magic("set_model", "my-model")
    ip.run_line_magic("code", "create a function")

    # Check if the function is now in the user's namespace
    assert "my_generated_function" in ip.user_ns