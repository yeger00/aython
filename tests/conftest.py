import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import MagicMock, patch


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_ipython_shell():
    """Create a mock IPython shell for testing magic commands."""
    shell = MagicMock()
    shell.user_ns = {"Out": {}}
    shell.execution_count = 1
    shell.history_manager = MagicMock()
    shell.history_manager.get_range.return_value = [
        (0, 1, "%init_aython gemini-1.5-flash"),
        (0, 2, "print('test')"),
        (0, 3, "%code 'create a function'"),
    ]
    return shell


@pytest.fixture
def mock_agent():
    """Create a mock AythonAgent for testing."""
    agent = MagicMock()
    agent.generate_and_execute.return_value = {
        "code_snippet": "print('Hello, World!')",
        "execution_result": MagicMock(exit_code=0, stdout="Hello, World!", stderr=""),
        "error": None
    }
    return agent


@pytest.fixture
def mock_agent_with_error():
    """Create a mock AythonAgent that returns an error."""
    agent = MagicMock()
    agent.generate_and_execute.return_value = {
        "code_snippet": "",
        "execution_result": None,
        "error": "API Error",
        "debug_log": "Detailed error message"
    }
    return agent


@pytest.fixture
def sample_code_snippet():
    """Sample code snippet for testing."""
    return """
def fibonacci(n):
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    else:
        list_fib = [0, 1]
        while len(list_fib) < n:
            next_fib = list_fib[-1] + list_fib[-2]
            list_fib.append(next_fib)
        return list_fib
"""


@pytest.fixture
def sample_notebook_data():
    """Sample notebook data for testing."""
    return {
        "cells": [
            {
                "cell_type": "code",
                "source": ["print('Hello, World!')"],
                "outputs": [
                    {
                        "output_type": "stream",
                        "name": "stdout",
                        "text": ["Hello, World!\n"]
                    }
                ],
                "execution_count": 1
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }


@pytest.fixture
def mock_requests_response():
    """Create a mock requests response for testing API calls."""
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {
        "jsonrpc": "2.0",
        "result": {"message": "Aython initialized with model gemini-1.5-flash"},
        "id": 1
    }
    return response


@pytest.fixture
def mock_requests_error():
    """Create a mock requests response with error for testing."""
    response = MagicMock()
    response.status_code = 500
    response.json.return_value = {
        "jsonrpc": "2.0",
        "error": {"code": -32000, "message": "Internal server error"},
        "id": 1
    }
    return response


@pytest.fixture(autouse=True)
def mock_environment():
    """Mock environment variables for testing."""
    with patch.dict(os.environ, {
        'AGENT_PORT': '4000',
        'MODEL': 'gemini-1.5-flash',
        'GOOGLE_API_KEY': 'test-key'
    }):
        yield


@pytest.fixture
def skip_if_no_api_key():
    """Skip test if no API key is available."""
    if not os.getenv('GOOGLE_API_KEY') and not os.getenv('OPENAI_API_KEY'):
        pytest.skip("No API key available for testing")


@pytest.fixture
def skip_if_no_docker():
    """Skip test if Docker is not available."""
    try:
        import docker
        client = docker.from_env()
        client.ping()
    except Exception:
        pytest.skip("Docker is not available for testing")


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests"
    )
    config.addinivalue_line(
        "markers", "e2e: End-to-end tests"
    )
    config.addinivalue_line(
        "markers", "docker: Docker-related tests"
    )
    config.addinivalue_line(
        "markers", "slow: Slow tests that take more than 30 seconds"
    )
    config.addinivalue_line(
        "markers", "api: Tests that require API keys"
    )
    config.addinivalue_line(
        "markers", "network: Tests that require network access"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Add markers based on test file names
        if "test_docker" in item.nodeid:
            item.add_marker(pytest.mark.docker)
        if "test_e2e" in item.nodeid:
            item.add_marker(pytest.mark.e2e)
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        
        # Add slow marker for tests that might take time
        if any(keyword in item.nodeid for keyword in ["docker", "e2e", "integration"]):
            item.add_marker(pytest.mark.slow)
        
        # Add API marker for tests that might need API keys
        if any(keyword in item.nodeid for keyword in ["agent", "generate", "api"]):
            item.add_marker(pytest.mark.api)
