import pytest
from unittest.mock import patch, MagicMock
from aython import AythonMagics


class MockIPythonShell:
    def __init__(self):
        self.user_ns = {"Out": {}}
        self.execution_count = 1
        self.history_manager = MagicMock()
        self.history_manager.get_range.return_value = [
            (0, 1, "%init_aython gemini-1.5-flash"),
            (0, 2, "print('hi')"),
        ]

    def run_cell(self, code):
        class Result:
            result = "executed"
        return Result()


@pytest.fixture
def ip():
    return MockIPythonShell()


def test_init_aython_magic(ip):
    """Test the %init_aython magic command."""
    with patch("aython.AythonAgent") as mock_agent_class:
        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent

        magics = AythonMagics(ip)
        magics.init_aython("gemini-1.5-flash")

        mock_agent_class.assert_called_once_with("gemini-1.5-flash")
        assert magics.aython == mock_agent


def test_code_magic_with_aython_agent(ip):
    """Test the %code magic command with mocked AythonAgent."""
    with patch("aython.AythonAgent") as mock_agent_class:
        mock_agent = MagicMock()
        mock_agent.code.return_value = MagicMock(code_snippet="print('hi')")
        mock_agent_class.return_value = mock_agent

        magics = AythonMagics(ip)
        magics.init_aython("gemini-1.5-flash")
        magics.code("say hello")

        mock_agent.code.assert_called_once_with("say hello")
        assert "generated code" in ip.user_ns["Out"][ip.execution_count]


def test_save_history(tmp_path, ip):
    """Test %save_history writes a file with history and outputs."""
    magics = AythonMagics(ip)
    outfile = tmp_path / "history.json"

    magics.save_history(str(outfile))

    assert outfile.exists()
    content = outfile.read_text()
    assert "%init_aython" in content


def test_export_notebook(tmp_path, ip):
    """Test %export_notebook writes a valid notebook file."""
    magics = AythonMagics(ip)
    outfile = tmp_path / "notebook.ipynb"

    magics.export_notebook(str(outfile))

    assert outfile.exists()
    content = outfile.read_text()
    assert "cells" in content
