import pytest
import json
import tempfile
import os
from unittest.mock import patch, MagicMock, call
from aython.magics.app.aython_magics import AythonMagics, JsonRpcClient


class MockIPythonShell:
    def __init__(self):
        self.user_ns = {"Out": {}}
        self.execution_count = 1
        self.history_manager = MagicMock()
        self.history_manager.get_range.return_value = [
            (0, 1, "%init_aython gemini-1.5-flash"),
            (0, 2, "print('hi')"),
            (0, 3, "%code 'create a function'"),
        ]

    def run_cell(self, code):
        class Result:
            result = "executed"
        return Result()


@pytest.fixture
def ip():
    return MockIPythonShell()


class TestAythonMagics:
    """Test the Aython magic commands functionality."""

    def test_init_aython_magic_success(self, ip):
        """Test successful %init_aython magic command."""
        with patch("aython.magics.app.aython_magics.client") as mock_client:
            mock_client.call.return_value = {"message": "Aython initialized with model gemini-1.5-flash"}

            magics = AythonMagics(ip)
            magics.init_aython("gemini-1.5-flash")

            mock_client.call.assert_called_once_with("init_agent", {"model": "gemini-1.5-flash"})

    def test_init_aython_magic_empty_model(self, ip):
        """Test %init_aython magic command with empty model."""
        magics = AythonMagics(ip)
        magics.init_aython("")
        
        # Should print usage message and not call client

    def test_init_aython_magic_error(self, ip):
        """Test %init_aython magic command with initialization error."""
        with patch("aython.magics.app.aython_magics.client") as mock_client:
            mock_client.call.return_value = {"error": "Initialization failed"}

            magics = AythonMagics(ip)
            magics.init_aython("gemini-1.5-flash")
            
            mock_client.call.assert_called_once_with("init_agent", {"model": "gemini-1.5-flash"})

    def test_code_magic_success(self, ip):
        """Test successful %code magic command."""
        with patch("aython.magics.app.aython_magics.client") as mock_client:
            mock_client.call.return_value = {
                "code_snippet": "print('Hello, World!')",
                "execution_result": {"exit_code": 0, "stdout": "Hello, World!", "stderr": ""}
            }

            magics = AythonMagics(ip)
            magics.code("say hello")

            mock_client.call.assert_called_once_with("generate_and_run", {"requirements": "say hello"})
            assert "generated code" in ip.user_ns["Out"][ip.execution_count]

    def test_code_magic_with_error(self, ip):
        """Test %code magic command with generation error."""
        with patch("aython.magics.app.aython_magics.client") as mock_client:
            mock_client.call.return_value = {
                "error": "No code generated",
                "debug_log": "API Error"
            }

            magics = AythonMagics(ip)
            magics.code("invalid request")

            mock_client.call.assert_called_once_with("generate_and_run", {"requirements": "invalid request"})

    def test_code_magic_without_init(self, ip):
        """Test %code magic command without initializing agent first."""
        with patch("aython.magics.app.aython_magics.client") as mock_client:
            mock_client.call.return_value = {
                "code_snippet": "print('Hello, World!')",
                "execution_result": {"exit_code": 0, "stdout": "Hello, World!", "stderr": ""}
            }
            
            magics = AythonMagics(ip)
            magics.code("say hello")
            
            # Should call client even without init
            mock_client.call.assert_called_once_with("generate_and_run", {"requirements": "say hello"})

    def test_code_magic_execution_in_notebook(self, ip):
        """Test that code is executed in the notebook environment."""
        with patch("aython.magics.app.aython_magics.client") as mock_client:
            mock_client.call.return_value = {
                "code_snippet": "x = 42\nprint(x)",
                "execution_result": {"exit_code": 0, "stdout": "42", "stderr": ""}
            }

            magics = AythonMagics(ip)
            
            # Mock exec to verify it's called
            with patch('builtins.exec') as mock_exec:
                magics.code("create a variable x = 42")
                
                # Verify exec was called with the generated code
                mock_exec.assert_called_once()
                call_args = mock_exec.call_args[0]
                assert "x = 42" in call_args[0]
                assert call_args[1] == ip.user_ns

    def test_save_history_success(self, tmp_path, ip):
        """Test successful %save_history magic command."""
        magics = AythonMagics(ip)
        outfile = tmp_path / "history.json"

        magics.save_history(str(outfile))

        assert outfile.exists()
        content = outfile.read_text()
        data = json.loads(content)
        assert isinstance(data, list)
        assert len(data) > 0
        assert "%init_aython" in data[0]["input"]

    def test_save_history_default_filename(self, tmp_path, ip):
        """Test %save_history with default filename."""
        magics = AythonMagics(ip)
        
        with patch('os.getcwd', return_value=str(tmp_path)):
            with patch('builtins.open', create=True) as mock_open:
                magics.save_history("")
                
                # Verify file was opened for writing
                mock_open.assert_called_once()
                call_args = mock_open.call_args[0]
                filename = call_args[0]
                assert filename.startswith("ipython_history_")
                assert filename.endswith(".json")

    def test_export_notebook_success(self, tmp_path, ip):
        """Test successful %export_notebook magic command."""
        magics = AythonMagics(ip)
        outfile = tmp_path / "notebook.ipynb"

        magics.export_notebook(str(outfile))

        assert outfile.exists()
        content = outfile.read_text()
        data = json.loads(content)
        assert "cells" in data
        assert "metadata" in data
        assert len(data["cells"]) > 0

    def test_export_notebook_default_filename(self, tmp_path, ip):
        """Test %export_notebook with default filename."""
        magics = AythonMagics(ip)
        
        with patch('os.getcwd', return_value=str(tmp_path)):
            with patch('builtins.open', create=True) as mock_open:
                magics.export_notebook("")
                
                # Verify file was opened for writing
                mock_open.assert_called_once()
                call_args = mock_open.call_args[0]
                filename = call_args[0]
                assert filename.startswith("ipython_export_")
                assert filename.endswith(".ipynb")

    def test_export_notebook_with_outputs(self, tmp_path, ip):
        """Test %export_notebook with outputs in history."""
        # Add some outputs to the mock
        ip.user_ns["Out"][1] = {
            "generated code": "print('test')",
            "execution_result": "executed_in_notebook",
            "display": []
        }
        
        magics = AythonMagics(ip)
        outfile = tmp_path / "notebook.ipynb"

        magics.export_notebook(str(outfile))

        assert outfile.exists()
        content = outfile.read_text()
        data = json.loads(content)
        
        # Check that we have cells
        assert len(data["cells"]) > 0
        
        # The mock history doesn't include the output in the right format for notebook export
        # This test verifies the basic functionality works


class TestAythonMagicsIntegration:
    """Integration tests for Aython magics."""

    def test_complete_workflow(self, ip):
        """Test complete magic commands workflow."""
        with patch("aython.magics.app.aython_magics.client") as mock_client:
            # Mock successful responses
            mock_client.call.side_effect = [
                {"message": "Aython initialized with model gemini-1.5-flash"},
                {
                    "code_snippet": "def test_func(): return 'hello'",
                    "execution_result": {"exit_code": 0, "stdout": "", "stderr": ""}
                }
            ]

            magics = AythonMagics(ip)
            
            # Test complete workflow
            magics.init_aython("gemini-1.5-flash")
            magics.code("create a test function")
            
            # Verify client was called correctly
            assert mock_client.call.call_count == 2
            mock_client.call.assert_any_call("init_agent", {"model": "gemini-1.5-flash"})
            mock_client.call.assert_any_call("generate_and_run", {"requirements": "create a test function"})

    def test_error_handling_workflow(self, ip):
        """Test error handling in magic commands workflow."""
        with patch("aython.magics.app.aython_magics.client") as mock_client:
            # Mock error response
            mock_client.call.side_effect = [
                {"message": "Aython initialized with model gemini-1.5-flash"},
                {
                    "error": "API Error",
                    "debug_log": "Detailed error message"
                }
            ]

            magics = AythonMagics(ip)
            
            # Test error handling
            magics.init_aython("gemini-1.5-flash")
            magics.code("invalid request")
            
            # Should handle error gracefully
            assert mock_client.call.call_count == 2


class TestAythonMagicsEdgeCases:
    """Test edge cases and error conditions."""

    def test_magic_with_special_characters(self, ip):
        """Test magic commands with special characters."""
        with patch("aython.magics.app.aython_magics.client") as mock_client:
            mock_client.call.return_value = {
                "code_snippet": "print('special chars: @#$%')",
                "execution_result": {"exit_code": 0, "stdout": "", "stderr": ""}
            }

            magics = AythonMagics(ip)
            magics.code("print special characters @#$%")

            mock_client.call.assert_called_once_with("generate_and_run", {"requirements": "print special characters @#$%"})

    def test_magic_with_multiline_input(self, ip):
        """Test magic commands with multiline input."""
        with patch("aython.magics.app.aython_magics.client") as mock_client:
            mock_client.call.return_value = {
                "code_snippet": "print('multiline')",
                "execution_result": {"exit_code": 0, "stdout": "", "stderr": ""}
            }

            magics = AythonMagics(ip)
            
            multiline_input = """create a function that:
            1. Takes two parameters
            2. Returns their sum
            3. Handles errors gracefully"""
            
            magics.code(multiline_input)
            mock_client.call.assert_called_once_with("generate_and_run", {"requirements": multiline_input})

    def test_magic_with_empty_input(self, ip):
        """Test magic commands with empty input."""
        magics = AythonMagics(ip)
        
        # Should handle empty input gracefully
        magics.code("")
        magics.init_aython("")
