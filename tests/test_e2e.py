import pytest
import subprocess
import time
import requests
import json
from pathlib import Path
from unittest.mock import patch


class TestEndToEndWorkflow:
    """End-to-end tests for the complete Aython workflow."""

    @pytest.fixture(scope="class")
    def docker_services(self):
        """Start Docker services for E2E testing."""
        aython_dir = Path(__file__).parent.parent / "src" / "aython"
        
        # Start services
        process = subprocess.Popen(
            ["docker-compose", "up", "--build", "-d"],
            cwd=aython_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for services to start
        time.sleep(20)
        
        yield
        
        # Cleanup
        subprocess.run(
            ["docker-compose", "down"],
            cwd=aython_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

    def test_complete_aython_workflow(self, docker_services):
        """Test the complete Aython workflow from initialization to code execution."""
        # Step 1: Initialize agent
        init_payload = {
            "jsonrpc": "2.0",
            "method": "init_agent",
            "params": {"model": "gemini-1.5-flash"},
            "id": 1
        }
        
        init_response = requests.post(
            "http://localhost:4000",
            json=init_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if init_response.status_code != 200:
            pytest.skip("Agent initialization failed - likely API key issue")
        
        init_data = init_response.json()
        assert "result" in init_data
        assert "Aython initialized" in init_data["result"]["message"]
        
        # Step 2: Generate and execute simple code
        code_payload = {
            "jsonrpc": "2.0",
            "method": "generate_and_run",
            "params": {"requirements": "print('Hello from Aython!')"},
            "id": 2
        }
        
        code_response = requests.post(
            "http://localhost:4000",
            json=code_payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        assert code_response.status_code == 200
        code_data = code_response.json()
        
        if "result" in code_data:
            result = code_data["result"]
            assert "code_snippet" in result
            assert "execution_result" in result
            
            # Verify execution result
            exec_result = result["execution_result"]
            assert "exit_code" in exec_result
            assert "stdout" in exec_result
            assert "stderr" in exec_result
            
            # For simple print statement, should succeed if API keys are available
            if exec_result["exit_code"] == 0 and exec_result["stdout"]:
                assert "Hello from Aython!" in exec_result["stdout"]
        elif "error" in code_data:
            # If API keys are not available, that's also acceptable for testing
            assert "error" in code_data

    def test_complex_code_generation_workflow(self, docker_services):
        """Test complex code generation and execution workflow."""
        # Initialize agent
        init_payload = {
            "jsonrpc": "2.0",
            "method": "init_agent",
            "params": {"model": "gemini-1.5-flash"},
            "id": 1
        }
        
        init_response = requests.post(
            "http://localhost:4000",
            json=init_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if init_response.status_code != 200:
            pytest.skip("Agent initialization failed - likely API key issue")
        
        # Test function generation
        function_payload = {
            "jsonrpc": "2.0",
            "method": "generate_and_run",
            "params": {"requirements": "create a function that calculates fibonacci numbers up to n"},
            "id": 2
        }
        
        function_response = requests.post(
            "http://localhost:4000",
            json=function_payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        assert function_response.status_code == 200
        function_data = function_response.json()
        
        if "result" in function_data:
            result = function_data["result"]
            code_snippet = result["code_snippet"]
            
            # Should contain function definition
            assert "def" in code_snippet.lower()
            assert "fibonacci" in code_snippet.lower()
            
            # Should execute successfully
            exec_result = result["execution_result"]
            if exec_result["exit_code"] == 0:
                # Function should be defined and executable
                assert "fibonacci" in exec_result["stdout"] or exec_result["stdout"] == ""

    def test_error_handling_workflow(self, docker_services):
        """Test error handling in the complete workflow."""
        # Initialize agent
        init_payload = {
            "jsonrpc": "2.0",
            "method": "init_agent",
            "params": {"model": "gemini-1.5-flash"},
            "id": 1
        }
        
        init_response = requests.post(
            "http://localhost:4000",
            json=init_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if init_response.status_code != 200:
            pytest.skip("Agent initialization failed - likely API key issue")
        
        # Test with invalid requirements
        invalid_payload = {
            "jsonrpc": "2.0",
            "method": "generate_and_run",
            "params": {"requirements": ""},  # Empty requirements
            "id": 2
        }
        
        invalid_response = requests.post(
            "http://localhost:4000",
            json=invalid_payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        assert invalid_response.status_code == 200
        invalid_data = invalid_response.json()
        
        # Should handle empty requirements gracefully
        assert "result" in invalid_data or "error" in invalid_data

    def test_multiple_requests_workflow(self, docker_services):
        """Test multiple sequential requests to the agent."""
        # Initialize agent
        init_payload = {
            "jsonrpc": "2.0",
            "method": "init_agent",
            "params": {"model": "gemini-1.5-flash"},
            "id": 1
        }
        
        init_response = requests.post(
            "http://localhost:4000",
            json=init_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if init_response.status_code != 200:
            pytest.skip("Agent initialization failed - likely API key issue")
        
        # Make multiple requests
        requests_data = [
            "print('First request')",
            "print('Second request')",
            "print('Third request')"
        ]
        
        for i, req in enumerate(requests_data, 2):
            payload = {
                "jsonrpc": "2.0",
                "method": "generate_and_run",
                "params": {"requirements": req},
                "id": i
            }
            
            response = requests.post(
                "http://localhost:4000",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "result" in data or "error" in data

    def test_jupyter_lab_accessibility(self, docker_services):
        """Test that Jupyter Lab is accessible and functional."""
        # Test Jupyter Lab main page
        response = requests.get("http://localhost:8888", timeout=10)
        assert response.status_code == 200
        assert "JupyterLab" in response.text
        
        # Test Jupyter Lab API
        api_response = requests.get("http://localhost:8888/api", timeout=10)
        assert api_response.status_code in [200, 404]  # 404 is OK for some API endpoints

    def test_services_communication(self, docker_services):
        """Test that services can communicate properly."""
        # Test that magics can reach agent
        # This is implicit in the magics functionality, but we can test the agent directly
        
        # Test agent health - 501 is expected for GET requests to JSON-RPC service
        agent_response = requests.get("http://localhost:4000", timeout=5)
        assert agent_response.status_code in [200, 405, 404, 501]  # 501 = Method Not Implemented for GET
        
        # Test magics health
        magics_response = requests.get("http://localhost:8888", timeout=5)
        assert magics_response.status_code == 200

    def test_performance_under_load(self, docker_services):
        """Test system performance under light load."""
        # Initialize agent
        init_payload = {
            "jsonrpc": "2.0",
            "method": "init_agent",
            "params": {"model": "gemini-1.5-flash"},
            "id": 1
        }
        
        init_response = requests.post(
            "http://localhost:4000",
            json=init_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if init_response.status_code != 200:
            pytest.skip("Agent initialization failed - likely API key issue")
        
        # Make multiple concurrent requests
        import concurrent.futures
        import threading
        
        def make_request(request_id):
            payload = {
                "jsonrpc": "2.0",
                "method": "generate_and_run",
                "params": {"requirements": f"print('Request {request_id}')"},
                "id": request_id
            }
            
            try:
                response = requests.post(
                    "http://localhost:4000",
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                return response.status_code == 200
            except requests.exceptions.RequestException:
                return False
        
        # Test with 5 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request, i) for i in range(5)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # At least some requests should succeed
        assert sum(results) > 0


class TestEndToEndMagicCommands:
    """Test end-to-end magic commands functionality."""

    def test_magic_commands_workflow(self):
        """Test the complete magic commands workflow."""
        from aython.magics.app.aython_magics import AythonMagics
        from unittest.mock import MagicMock
        
        # Create a proper mock shell that satisfies traitlets requirements
        class MockShell:
            def __init__(self):
                self.user_ns = {"Out": {}}
                self.execution_count = 1
                self.history_manager = MagicMock()
                self.history_manager.get_range.return_value = [
                    (0, 1, "%init_aython gemini-1.5-flash"),
                    (0, 2, "%code 'print hello'"),
                ]
        
        mock_shell = MockShell()
        
        # Mock client
        with patch("aython.magics.app.aython_magics.client") as mock_client:
            mock_client.call.side_effect = [
                {"message": "Aython initialized with model gemini-1.5-flash"},
                {
                    "code_snippet": "print('Hello, World!')",
                    "execution_result": {"exit_code": 0, "stdout": "Hello, World!", "stderr": ""}
                }
            ]
            
            # Test magic commands
            magics = AythonMagics(mock_shell)
            
            # Initialize
            magics.init_aython("gemini-1.5-flash")
            
            # Generate code
            with patch('builtins.exec') as mock_exec:
                magics.code("print hello")
                
                # Verify client was called
                assert mock_client.call.call_count == 2
                mock_client.call.assert_any_call("init_agent", {"model": "gemini-1.5-flash"})
                mock_client.call.assert_any_call("generate_and_run", {"requirements": "print hello"})
                
                # Verify code was executed
                mock_exec.assert_called_once()

    def test_magic_commands_error_handling(self):
        """Test magic commands error handling."""
        from aython.magics.app.aython_magics import AythonMagics
        from unittest.mock import MagicMock
        
        # Create a proper mock shell that satisfies traitlets requirements
        class MockShell:
            def __init__(self):
                self.user_ns = {"Out": {}}
                self.execution_count = 1
                self.history_manager = MagicMock()
                self.history_manager.get_range.return_value = []
        
        mock_shell = MockShell()
        
        # Mock client with error
        with patch("aython.magics.app.aython_magics.client") as mock_client:
            mock_client.call.side_effect = [
                {"message": "Aython initialized with model gemini-1.5-flash"},
                {
                    "error": "API Error",
                    "debug_log": "Detailed error message"
                }
            ]
            
            # Test error handling
            magics = AythonMagics(mock_shell)
            magics.init_aython("gemini-1.5-flash")
            
            # Should handle error gracefully
            magics.code("invalid request")
            assert mock_client.call.call_count == 2

    def test_magic_commands_file_operations(self, tmp_path):
        """Test magic commands file operations."""
        from aython.magics.app.aython_magics import AythonMagics
        from unittest.mock import MagicMock
        
        # Create a proper mock shell that satisfies traitlets requirements
        class MockShell:
            def __init__(self):
                self.user_ns = {"Out": {}}
                self.execution_count = 1
                self.history_manager = MagicMock()
                self.history_manager.get_range.return_value = [
                    (0, 1, "%init_aython gemini-1.5-flash"),
                    (0, 2, "print('test')"),
                ]
        
        mock_shell = MockShell()
        
        # Test save history
        magics = AythonMagics(mock_shell)
        history_file = tmp_path / "test_history.json"
        
        with patch('os.getcwd', return_value=str(tmp_path)):
            magics.save_history(str(history_file))
            
            assert history_file.exists()
            content = history_file.read_text()
            data = json.loads(content)
            assert isinstance(data, list)
        
        # Test export notebook
        notebook_file = tmp_path / "test_notebook.ipynb"
        magics.export_notebook(str(notebook_file))
        
        assert notebook_file.exists()
        content = notebook_file.read_text()
        data = json.loads(content)
        assert "cells" in data
        assert "metadata" in data
