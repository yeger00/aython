# Aython

![Tests](https://github.com/yeger00/aython/actions/workflows/test.yml/badge.svg)

A Warp-like Python command palette built with Textual. Execute Python commands in a beautiful TUI environment, combining the power of Python with the elegance of Warp's interface.

## Quick Start

### Installation
```bash
# Clone the repository
git clone https://github.com/yeger00/aython.git
cd aython

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .

# Run the application
aython
```

## Development

### Running Tests

First, make sure you have the development dependencies installed:
```bash
# Install with dev dependencies
uv pip install -e .[dev]
```

Then you can run the tests:
```bash
# Run all tests
pytest

# Run tests with output
pytest -v

# Run tests with coverage
pytest --cov=aython
```

### Continuous Integration

The project uses GitHub Actions to run tests automatically on:
- Pull request creation
- Pull request updates
- Pushes to main branch

The CI pipeline:
- Runs tests on Python 3.9, 3.10, and 3.11
- Uses uv for fast dependency installation
- Generates and uploads test coverage reports
- Caches virtual environments for faster builds
