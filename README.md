# Aython

![Tests](https://github.com/yeger00/aython/actions/workflows/test.yml/badge.svg)

A Warp-like Python command palette built with Textual. Execute Python commands in a beautiful TUI environment, combining the power of Python with the elegance of Warp's interface.

## Quick Start

### Installation
```bash
# Clone the repository
git clone https://github.com/yeger00/aython.git
cd aython
# Install with poetry
poetry install
# Run the application
poetry run aython
```

## Development

### Running Tests

First, make sure you have the development dependencies installed:
```bash

# Install with dev dependencies
poetry install --with dev
```

Then you can run the tests:
```bash
# Run all tests
poetry run pytest
# Run tests with output
poetry run pytest -v
# Run tests with coverage
poetry run pytest --cov=aython
```

### Continuous Integration

The project uses GitHub Actions to run tests automatically on:
- Pull request creation
- Pull request updates
- Pushes to main branch

The CI pipeline:
- Runs tests on Python 3.8, 3.9, 3.10, and 3.11
- Generates and uploads test coverage reports
- Caches dependencies for faster builds
