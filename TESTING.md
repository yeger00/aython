# Aython Testing Guide

This document describes the comprehensive testing strategy for the Aython project.

## 🧪 Test Structure

### Test Categories

1. **Unit Tests** (`tests/test_aython.py`)
   - Test individual components in isolation
   - Mock external dependencies
   - Fast execution
   - High coverage

2. **Integration Tests** (`tests/test_docker_integration.py`)
   - Test Docker services integration
   - Test service communication
   - Test container health
   - Medium execution time

3. **End-to-End Tests** (`tests/test_e2e.py`)
   - Test complete workflows
   - Test real API interactions
   - Test magic commands functionality
   - Slow execution time

## 🚀 Running Tests

### Quick Start

```bash
# Run quick tests (unit tests only, no Docker/API)
python run_tests.py --type quick

# Run all tests with coverage
python run_tests.py --type all --coverage

# Run specific test type
python run_tests.py --type unit
python run_tests.py --type integration
python run_tests.py --type e2e
```

### Using pytest directly

```bash
# Unit tests only
pytest tests/test_aython.py -v

# Integration tests
pytest tests/test_docker_integration.py -v

# End-to-end tests
pytest tests/test_e2e.py -v

# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=aython --cov-report=html
```

### Test Markers

Tests are organized using pytest markers:

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only end-to-end tests
pytest -m e2e

# Run only Docker tests
pytest -m docker

# Run only API tests
pytest -m api

# Skip slow tests
pytest -m "not slow"

# Skip Docker tests
pytest -m "not docker"
```

## 📋 Test Coverage

### Unit Tests Coverage

- **Agent Functionality** (`TestAgentAPI`, `TestAgentExecution`, `TestAgentCodeGeneration`)
  - JSON-RPC API endpoints
  - Code execution capabilities
  - Code generation with retries
  - Error handling

- **Magic Commands** (`TestAythonMagics`)
  - `%init_aython` command
  - `%code` command with execution
  - `%save_history` command
  - `%export_notebook` command
  - Error handling and edge cases

- **Integration Workflows** (`TestAythonMagicsIntegration`)
  - Complete magic commands workflow
  - Error handling workflows
  - Edge cases and special characters

### Integration Tests Coverage

- **Docker Services** (`TestDockerIntegration`)
  - Service startup and health
  - API endpoint accessibility
  - Service communication
  - Container isolation

- **Service Configuration** (`TestDockerConfiguration`)
  - Docker Compose configuration validity
  - Dockerfile syntax validation
  - Environment variable documentation

### End-to-End Tests Coverage

- **Complete Workflows** (`TestEndToEndWorkflow`)
  - Agent initialization to code execution
  - Complex code generation workflows
  - Error handling workflows
  - Multiple sequential requests
  - Performance under load

- **Magic Commands E2E** (`TestEndToEndMagicCommands`)
  - Complete magic commands workflow
  - File operations (save/export)
  - Error handling in magic commands

## 🔧 Test Configuration

### Environment Variables

Tests use the following environment variables:

```bash
# Required for API tests
GOOGLE_API_KEY=your_google_api_key
OPENAI_API_KEY=your_openai_api_key

# Optional configuration
AGENT_PORT=4000
MODEL=gemini-1.5-flash
```

### Test Fixtures

Common test fixtures are defined in `tests/conftest.py`:

- `mock_ipython_shell`: Mock IPython shell for magic commands
- `mock_agent`: Mock AythonAgent for testing
- `mock_agent_with_error`: Mock agent that returns errors
- `sample_code_snippet`: Sample code for testing
- `sample_notebook_data`: Sample notebook data
- `temp_dir`: Temporary directory for test files

## 🐳 Docker Testing

### Prerequisites

- Docker and Docker Compose installed
- Sufficient system resources for containers

### Running Docker Tests

```bash
# Run integration tests (includes Docker)
python run_tests.py --type integration --docker

# Run all tests including Docker
python run_tests.py --type all --docker
```

### Docker Test Environment

Docker tests automatically:
- Start required services
- Wait for services to be ready
- Run tests against running containers
- Clean up containers after tests

## 📊 Coverage Reports

### Generating Coverage

```bash
# Generate HTML coverage report
pytest tests/ --cov=aython --cov-report=html

# Generate XML coverage report (for CI)
pytest tests/ --cov=aython --cov-report=xml

# Generate both
pytest tests/ --cov=aython --cov-report=html --cov-report=xml
```

### Coverage Reports Location

- HTML report: `htmlcov/index.html`
- XML report: `coverage.xml`
- Terminal output: Shows coverage summary

## 🚨 CI/CD Testing

### GitHub Actions Workflow

The project uses GitHub Actions for continuous integration:

1. **Unit Tests**: Run on Python 3.9, 3.10, 3.11
2. **Integration Tests**: Test Docker services
3. **End-to-End Tests**: Full workflow testing (main branch only)
4. **Lint and Format**: Code quality checks
5. **Security Scan**: Security vulnerability scanning
6. **Docker Build**: Test Docker image builds

### Test Matrix

| Test Type | Python Versions | Docker | API Keys | Frequency |
|-----------|----------------|--------|----------|-----------|
| Unit | 3.9, 3.10, 3.11 | ❌ | ❌ | Every push/PR |
| Integration | 3.11 | ✅ | ❌ | Every push/PR |
| E2E | 3.11 | ✅ | ✅ | Main branch only |
| Lint | 3.11 | ❌ | ❌ | Every push/PR |
| Security | 3.11 | ❌ | ❌ | Every push/PR |
| Docker Build | N/A | ✅ | ❌ | Every push/PR |

## 🐛 Debugging Tests

### Verbose Output

```bash
# Run with verbose output
pytest tests/ -v -s

# Run specific test with verbose output
pytest tests/test_aython.py::TestAythonMagics::test_code_magic_success -v -s
```

### Debug Mode

```bash
# Run with Python debugger
pytest tests/ --pdb

# Run with debug output
pytest tests/ --log-cli-level=DEBUG
```

### Test Isolation

```bash
# Run tests in isolation (no shared state)
pytest tests/ --forked

# Run tests in random order
pytest tests/ --random-order
```

## 📈 Performance Testing

### Load Testing

```bash
# Run performance tests
pytest tests/test_e2e.py::TestEndToEndWorkflow::test_performance_under_load -v
```

### Memory Testing

```bash
# Run with memory profiling
pytest tests/ --memray
```

## 🔍 Test Maintenance

### Adding New Tests

1. **Unit Tests**: Add to `tests/test_aython.py`
2. **Integration Tests**: Add to `tests/test_docker_integration.py`
3. **E2E Tests**: Add to `tests/test_e2e.py`

### Test Naming Convention

- Test files: `test_*.py`
- Test classes: `Test*`
- Test methods: `test_*`
- Use descriptive names that explain what is being tested

### Test Documentation

- Each test should have a docstring explaining its purpose
- Use clear, descriptive test names
- Group related tests in classes
- Use appropriate pytest markers

## 🎯 Best Practices

### Test Design

1. **Arrange-Act-Assert**: Structure tests clearly
2. **One Assertion Per Test**: Test one thing at a time
3. **Descriptive Names**: Use clear, descriptive test names
4. **Independent Tests**: Tests should not depend on each other
5. **Fast Tests**: Unit tests should be fast
6. **Mock External Dependencies**: Don't make real API calls in unit tests

### Test Data

1. **Use Fixtures**: Reuse common test data
2. **Minimal Data**: Use only necessary test data
3. **Clean Up**: Clean up after tests
4. **Isolated Data**: Use unique data for each test

### Error Testing

1. **Test Error Cases**: Test both success and failure scenarios
2. **Test Edge Cases**: Test boundary conditions
3. **Test Invalid Input**: Test with invalid inputs
4. **Test Network Failures**: Test network error scenarios

## 📚 Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [Docker Testing Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Python Testing Best Practices](https://docs.python.org/3/library/unittest.html)
