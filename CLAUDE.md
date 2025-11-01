# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

FmailerSDK is a Python SDK for the Fmailer email service API (api.fmailer.ru). It provides both synchronous and asynchronous methods for sending emails via templates or simple HTML content.

## Architecture

### Core Components

1. **FmailerSdk class** (`sdk.py`):
   - Main SDK class handling both sync and async email operations
   - Uses lazy-initialized ThreadPoolExecutor for async operations
   - Supports idempotency keys to prevent duplicate sends
   - Two main sending modes:
     - `send_simple()` / `send_simple_async()`: Send HTML emails directly
     - `send()` / `send_async()`: Send templated emails with parameters

2. **Exception handling** (`exceptions.py`):
   - Single custom exception: `FmailerSdkException`
   - Used for both API errors and network failures

3. **Import structure** (`__init__.py`):
   - Package is currently minimal (single line file)
   - Note: Import paths in code reference `fmailerdjango.fmailersdk.*` which suggests this was extracted from a Django project

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

Activate the virtual environment first, then run tests with the proper PYTHONPATH:

```bash
source .venv/bin/activate
PYTHONPATH=/Users/skyman/Documents/My/Python:$PYTHONPATH python -m unittest tests
```

Run specific test class:
```bash
source .venv/bin/activate
PYTHONPATH=/Users/skyman/Documents/My/Python:$PYTHONPATH python -m unittest tests.FmailersdkTestUtils
PYTHONPATH=/Users/skyman/Documents/My/Python:$PYTHONPATH python -m unittest tests.FmailersdkAsyncTestUtils
```

Run specific test:
```bash
source .venv/bin/activate
PYTHONPATH=/Users/skyman/Documents/My/Python:$PYTHONPATH python -m unittest tests.FmailersdkAsyncTestUtils.test_send_simple_async_success
```

### Test Structure

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

### Import Path Issue

**CRITICAL**: The codebase has hardcoded import paths:
```python
from fmailerdjango.fmailersdk.exceptions import FmailerSdkException
from fmailerdjango.fmailersdk.sdk import FmailerSdk
```

This suggests the code was extracted from a `fmailerdjango` parent package. When modifying imports or creating new files, be aware that:
- Current imports expect the package to be at `fmailerdjango.fmailersdk`
- To make this a standalone package, imports would need to be changed to `from fmailersdk.` or relative imports
