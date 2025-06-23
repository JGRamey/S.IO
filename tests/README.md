# Yggdrasil Test Suite

This directory contains comprehensive tests for the Yggdrasil S.IO system.

## Test Structure

### Core Test Files

- **`conftest.py`** - Pytest configuration and fixtures
- **`test_config.py`** - Test configuration utilities and sample data
- **`quick_agent_test.py`** - Quick MCP agent integration test

### Unit Tests (Fast, No Dependencies)

- **`test_config_unit.py`** - Unit tests for configuration management
- **`test_utils_unit.py`** - Unit tests for utility functions
- **`test_agents_mock.py`** - Mock tests for agents (no external deps)

### Integration Tests (Requires Services)

- **`test_integration.py`** - Full system integration tests
- **`test_mcp_agents.py`** - MCP agent integration tests

### Specialized Tests

- **`test_bias_standalone.py`** - Standalone bias detection tests

## Running Tests

### Using pytest directly:
```bash
# Run all tests
pytest

# Run only unit tests (fast)
pytest -m unit

# Run only integration tests
pytest -m integration

# Run with coverage
pytest --cov=yggdrasil
```

### Using the test runner:
```bash
# Run all tests
python run_tests.py

# Run only unit tests
python run_tests.py unit

# Run quick tests with fail-fast
python run_tests.py quick

# Run with coverage
python run_tests.py all --coverage
```

## Test Categories

Tests are marked with pytest markers:

- `@pytest.mark.unit` - Fast unit tests, no external dependencies
- `@pytest.mark.integration` - Integration tests requiring services
- `@pytest.mark.slow` - Tests that take >10 seconds
- `@pytest.mark.database` - Tests requiring database connection
- `@pytest.mark.mcp` - MCP server/client tests
- `@pytest.mark.ai` - Tests requiring AI models

## Test Configuration

Test configuration is centralized in `test_config.py`:
- Environment-based settings
- Sample texts for consistent testing
- Test database configuration
- Reusable test utilities

## Dependencies

Make sure to install test dependencies:
```bash
pip install pytest pytest-asyncio pytest-cov
```

For Docker-based testing:
```bash
cd deployment/docker && ./docker-setup.sh start
```
