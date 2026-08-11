# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

PostwingSDK is a Python SDK for the Postwing email service API (api.postwing.app). It provides both synchronous and asynchronous methods for sending emails via templates or simple HTML content.

## Project Structure

```
postwing/
├── src/
│   └── postwing/          # Main package source
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

1. **PostwingSdk class** (`src/postwing/sdk.py`):
   - Main SDK class handling both sync and async email operations
   - Uses lazy-initialized ThreadPoolExecutor for async operations
   - Supports idempotency keys to prevent duplicate sends
   - Comprehensive logging with configurable log levels
   - Two main sending modes:
     - `send_simple()` / `send_simple_async()`: Send HTML emails directly
     - `send()` / `send_async()`: Send templated emails with parameters
   - **Optional payload fields are omitted, not sent as null.** `reply_to`,
     `headers`, `text` and `mass_mail` are added to the payload only when the
     caller sets them, because this client gets installed against API
     deployments older than the field, and an unknown key is rejected rather
     than ignored. The test for any new field is therefore two cases: present
     when set, *absent* when not
   - `text` is the `text/plain` alternative to `body`'s HTML; omitted, the API
     derives one. On the templated methods it is used verbatim — `params` are
     substituted into the template body, never into `text`
   - `mass_mail=True` attaches the one-click unsubscribe headers bulk senders
     need. One-way: `False` does not remove them, it defers to the API's own
     classifier, so it is a tri-state and `False` must still reach the wire

2. **Exception handling** (`src/postwing/exceptions.py`):
   - Single custom exception: `PostwingSdkException`
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
make test-specific TEST=tests.test_sdk.PostwingAsyncTestUtils.test_send_simple_async_success
```

Or manually, with `src` on the path so the suite tests this working tree
rather than whatever `postwing` happens to be installed in the environment:

```bash
source .venv/bin/activate
PYTHONPATH=src:$PYTHONPATH python -m unittest discover -s tests
```

Run specific test class:
```bash
source .venv/bin/activate
PYTHONPATH=src:$PYTHONPATH python -m unittest tests.test_sdk.PostwingTestUtils
PYTHONPATH=src:$PYTHONPATH python -m unittest tests.test_sdk.PostwingAsyncTestUtils
```

### Test Structure

Located in `tests/test_sdk.py`:

- `PostwingTestUtils`: Tests for synchronous methods
- `PostwingAsyncTestUtils`: Comprehensive async method tests including callbacks, futures, concurrent execution, and executor lifecycle

All tests use mocked `requests.post` to avoid actual API calls.

## Important Implementation Details

### Authentication

The SDK uses basic auth passed in the JSON payload:
```python
auth = {"username": username, "password": password}
```

### API Endpoints

- Base URL: `https://api.postwing.app/external/`
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
from postwing.sdk import PostwingSdk
from postwing.exceptions import PostwingSdkException
```

Internal imports within the package use relative imports:
```python
from .exceptions import PostwingSdkException
```
