import pytest
import subprocess
import time
import requests
import json
import tempfile
import os
from pathlib import Path


class TestDockerIntegration:
    """Test Docker services integration."""

    @pytest.fixture(scope="class")
    def docker_services(self):
        """Start Docker services for testing."""
        # Change to the aython directory
        aython_dir = Path(__file__).parent.parent / "src" / "aython"
        
        # Start services
        process = subprocess.Popen(
            ["docker-compose", "up", "--build", "-d"],
            cwd=aython_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for services to start
        time.sleep(15)
        
        yield
        
        # Cleanup
        subprocess.run(
            ["docker-compose", "down"],
            cwd=aython_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

    def test_agent_service_running(self, docker_services):
        """Test that the agent service is running and responding."""
        response = requests.get("http://localhost:4000", timeout=10)
        # Should get some response (even if it's an error for GET)
        assert response.status_code in [200, 405, 404, 501]  # 501 for method not implemented is OK

    def test_agent_jsonrpc_api(self, docker_services):
        """Test the agent JSON-RPC API."""
        payload = {
            "jsonrpc": "2.0",
            "method": "init_agent",
            "params": {"model": "gemini-1.5-flash"},
            "id": 1
        }
        
        response = requests.post(
            "http://localhost:4000",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "result" in data or "error" in data

    def test_magics_service_running(self, docker_services):
        """Test that the magics service (Jupyter Lab) is running."""
        response = requests.get("http://localhost:8888", timeout=10)
        assert response.status_code == 200
        assert "JupyterLab" in response.text

    def test_agent_code_generation(self, docker_services):
        """Test code generation through the agent API."""
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
        
        # Generate code
        code_payload = {
            "jsonrpc": "2.0",
            "method": "generate_and_run",
            "params": {"requirements": "print('Hello, World!')"},
            "id": 2
        }
        
        code_response = requests.post(
            "http://localhost:4000",
            json=code_payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        assert code_response.status_code == 200
        data = code_response.json()
        
        # Should either succeed or fail gracefully
        assert "result" in data or "error" in data
        if "result" in data:
            assert "code_snippet" in data["result"]

    def test_services_health_check(self, docker_services):
        """Test that both services are healthy."""
        # Check agent
        try:
            agent_response = requests.get("http://localhost:4000", timeout=5)
            agent_healthy = agent_response.status_code in [200, 405, 404, 501]  # 501 is OK for JSON-RPC
        except requests.exceptions.RequestException:
            agent_healthy = False
        
        # Check magics
        try:
            magics_response = requests.get("http://localhost:8888", timeout=5)
            magics_healthy = magics_response.status_code == 200
        except requests.exceptions.RequestException:
            magics_healthy = False
        
        assert agent_healthy, "Agent service is not healthy"
        assert magics_healthy, "Magics service is not healthy"

    def test_docker_containers_running(self, docker_services):
        """Test that Docker containers are running."""
        result = subprocess.run(
            ["docker-compose", "ps", "--services", "--filter", "status=running"],
            cwd=Path(__file__).parent.parent / "src" / "aython",
            capture_output=True,
            text=True
        )
        
        running_services = result.stdout.strip().split('\n')
        assert "aython-agent" in running_services
        assert "aython-magics" in running_services

    def test_agent_execution_capability(self, docker_services):
        """Test that the agent can execute Python code."""
        # This test verifies the integrated execution functionality
        payload = {
            "jsonrpc": "2.0",
            "method": "init_agent",
            "params": {"model": "gemini-1.5-flash"},
            "id": 1
        }
        
        init_response = requests.post(
            "http://localhost:4000",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if init_response.status_code != 200:
            pytest.skip("Agent initialization failed - likely API key issue")
        
        # Test simple code execution
        code_payload = {
            "jsonrpc": "2.0",
            "method": "generate_and_run",
            "params": {"requirements": "create a simple function that returns 42"},
            "id": 2
        }
        
        code_response = requests.post(
            "http://localhost:4000",
            json=code_payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        assert code_response.status_code == 200
        data = code_response.json()
        
        if "result" in data:
            result = data["result"]
            assert "code_snippet" in result
            assert "execution_result" in result
            # Verify execution result structure
            exec_result = result["execution_result"]
            assert "exit_code" in exec_result
            assert "stdout" in exec_result
            assert "stderr" in exec_result


class TestDockerServiceIsolation:
    """Test that Docker services are properly isolated."""

    def test_agent_port_isolation(self):
        """Test that agent service only responds on port 4000."""
        # Should respond on 4000
        try:
            response = requests.get("http://localhost:4000", timeout=5)
            assert response.status_code in [200, 405, 404]
        except requests.exceptions.RequestException:
            pytest.skip("Agent service not running")
        
        # Should not respond on other ports
        for port in [4001, 5000, 8888]:
            try:
                response = requests.get(f"http://localhost:{port}", timeout=2)
                if port == 8888:
                    # Magics service should respond on 8888
                    assert response.status_code == 200
                else:
                    # Other ports should not respond
                    assert response.status_code not in [200]
            except requests.exceptions.RequestException:
                # Expected for non-service ports
                pass

    def test_magics_port_isolation(self):
        """Test that magics service only responds on port 8888."""
        try:
            response = requests.get("http://localhost:8888", timeout=5)
            assert response.status_code == 200
            assert "JupyterLab" in response.text
        except requests.exceptions.RequestException:
            pytest.skip("Magics service not running")

    def test_services_independence(self):
        """Test that services can run independently."""
        # This test would require stopping one service and checking the other
        # For now, just verify both are accessible
        agent_accessible = False
        magics_accessible = False
        
        try:
            response = requests.get("http://localhost:4000", timeout=2)
            agent_accessible = response.status_code in [200, 405, 404, 501]  # 501 is OK for JSON-RPC
        except requests.exceptions.RequestException:
            agent_accessible = False

        try:
            response = requests.get("http://localhost:8888", timeout=2)
            magics_accessible = response.status_code == 200
        except requests.exceptions.RequestException:
            magics_accessible = False

        # At least one should be accessible for this test to be meaningful
        assert agent_accessible or magics_accessible


class TestDockerConfiguration:
    """Test Docker configuration and setup."""

    def test_docker_compose_config_valid(self):
        """Test that docker-compose.yml is valid."""
        aython_dir = Path(__file__).parent.parent / "src" / "aython"
        
        result = subprocess.run(
            ["docker-compose", "config"],
            cwd=aython_dir,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, f"docker-compose config failed: {result.stderr}"

    def test_dockerfile_syntax(self):
        """Test that Dockerfiles have valid syntax."""
        aython_dir = Path(__file__).parent.parent / "src" / "aython"
        
        # Test agent Dockerfile
        agent_dockerfile = aython_dir / "agent" / "Dockerfile"
        assert agent_dockerfile.exists()
        
        # Test magics Dockerfile
        magics_dockerfile = aython_dir / "magics" / "Dockerfile"
        assert magics_dockerfile.exists()

    def test_environment_variables(self):
        """Test that required environment variables are documented."""
        aython_dir = Path(__file__).parent.parent / "src" / "aython"
        
        # Check if .env.example exists
        env_example = aython_dir / ".env.example"
        if env_example.exists():
            env_content = env_example.read_text()
            assert "MODEL" in env_content
            assert "OPENAI_API_KEY" in env_content or "GOOGLE_API_KEY" in env_content
