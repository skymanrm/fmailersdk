# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

FmailerSDK is a Python SDK for the Fmailer email service API (api.fmailer.ru). It provides both synchronous and asynchronous methods for sending emails via templates or simple HTML content.

## Project Structure

```
fmailersdk/
├── src/
│   └── fmailersdk/          # Main package source
│       ├── __init__.py      # Package initialization
│       ├── sdk.py           # Core SDK implementation
│       └── exceptions.py    # Custom exceptions
├── tests/
│   ├── __init__.py
│   └── test_sdk.py          # Test suite (sync + async tests)
├── examples/
│   ├── async_example.py     # Async usage examples
│   └── logging_example.py   # Logging configuration examples
├── pyproject.toml           # Project configuration
├── Makefile                 # Development commands
└── README.md                # User documentation
```

## Architecture

### Core Components

1. **FmailerSdk class** (`src/fmailersdk/sdk.py`):
   - Main SDK class handling both sync and async email operations
   - Uses lazy-initialized ThreadPoolExecutor for async operations
   - Supports idempotency keys to prevent duplicate sends
   - Comprehensive logging with configurable log levels
   - Two main sending modes:
     - `send_simple()` / `send_simple_async()`: Send HTML emails directly
     - `send()` / `send_async()`: Send templated emails with parameters

2. **Exception handling** (`src/fmailersdk/exceptions.py`):
   - Single custom exception: `FmailerSdkException`
   - Used for both API errors and network failures

3. **Logging**:
   - Configurable log level via `log_level` parameter in SDK initialization
   - DEBUG level: Full request/response details with sanitized credentials
   - INFO level: Operational messages (initialization, sends, shutdown)
   - ERROR level: API errors, network failures, task failures

### Key Design Patterns

- **Lazy initialization**: ThreadPoolExecutor is created only when first async method is called
- **Resource cleanup**: SDK provides `shutdown()` method and `__del__` for executor cleanup
- **Fail silently mode**: Constructor accepts `fail_silently` flag to suppress exceptions
- **Callback support**: Async methods accept optional callbacks called with `(result, exception)`

## Setup

### Installing Dependencies

```bash
pip install -r requirements.txt
```

Dependencies:
- `requests`: Required for making HTTP API calls
- `faker`: Required for running tests (generates fake email addresses)

## Testing

### Running Tests

The easiest way to run tests is using the Makefile:

```bash
# Run all tests
make test

# Run synchronous tests only
make test-sync

# Run asynchronous tests only
make test-async

# Run a specific test
make test-specific TEST=tests.test_sdk.FmailersdkAsyncTestUtils.test_send_simple_async_success
```

Or manually with proper PYTHONPATH:

```bash
source .venv/bin/activate
PYTHONPATH=/Users/skyman/Documents/My/Python:$PYTHONPATH python -m unittest discover -s tests
```

Run specific test class:
```bash
source .venv/bin/activate
PYTHONPATH=/Users/skyman/Documents/My/Python:$PYTHONPATH python -m unittest tests.test_sdk.FmailersdkTestUtils
PYTHONPATH=/Users/skyman/Documents/My/Python:$PYTHONPATH python -m unittest tests.test_sdk.FmailersdkAsyncTestUtils
```

### Test Structure

Located in `tests/test_sdk.py`:

- `FmailersdkTestUtils`: Tests for synchronous methods
- `FmailersdkAsyncTestUtils`: Comprehensive async method tests including callbacks, futures, concurrent execution, and executor lifecycle

All tests use mocked `requests.post` to avoid actual API calls.

## Important Implementation Details

### Authentication

The SDK uses basic auth passed in the JSON payload:
```python
auth = {"username": username, "password": password}
```

### API Endpoints

- Base URL: `https://api.fmailer.ru/external/`
- Simple send: `POST /external/send_email_simple/`
- Template send: `POST /external/send_email_tpl/`

### Async Implementation

- Uses `concurrent.futures.ThreadPoolExecutor` (not asyncio)
- Default 5 workers, configurable via `max_workers` parameter
- Returns `Future` objects that can be:
  - Waited on with `future.result(timeout=N)`
  - Checked with `future.done()`
  - Used with callbacks for fire-and-forget patterns

### Import Structure

The package uses a standard src/ layout:
```python
from fmailersdk.sdk import FmailerSdk
from fmailersdk.exceptions import FmailerSdkException
```

Internal imports within the package use relative imports:
```python
from .exceptions import FmailerSdkException
```
