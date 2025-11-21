# FmailerSDK

A Python SDK for the [Fmailer](https://fmailer.ru) email service API. Provides both synchronous and asynchronous methods for sending emails via templates or simple HTML content.

## Features

- **Synchronous and Asynchronous API** - Choose between blocking and non-blocking email sending
- **Template Support** - Send emails using pre-configured templates with parameters
- **Simple HTML Emails** - Send plain HTML emails directly
- **Idempotency Keys** - Prevent duplicate email sends with unique keys
- **Multi-language Support** - Send templated emails in different languages
- **Thread Pool Execution** - Efficient concurrent email sending with configurable worker threads
- **Callback Support** - Handle async results with callbacks for fire-and-forget patterns
- **Fail Silently Mode** - Option to suppress exceptions for graceful degradation
- **Comprehensive Logging** - Configurable logging levels with detailed request/response information for debugging

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

### Dependencies

- `requests` - For making HTTP API calls
- `faker` - For running tests (development only)

## Quick Start

```python
from fmailersdk.sdk import FmailerSdk

# Initialize the SDK
sdk = FmailerSdk(
    username="your-domain@example.com",
    password="your-api-token"
)

# Send a simple HTML email
sdk.send_simple(
    recipient="user@example.com",
    sender="noreply@example.com",
    subject="Welcome!",
    body="<h1>Hello World</h1>"
)

# Send a templated email
sdk.send(
    tpl="welcome-template",
    recipient="user@example.com",
    sender="noreply@example.com",
    lang="en",
    params={"name": "John", "code": "123456"}
)
```

## Usage

### Synchronous Methods

#### Send Simple HTML Email

```python
sdk.send_simple(
    recipient="user@example.com",
    sender="noreply@example.com",
    subject="Important Notice",
    body="<p>This is an important message.</p>",
    idempotency_key="unique-key-123"  # Optional: prevent duplicates
)
```

#### Send Templated Email

```python
sdk.send(
    tpl="password-reset",
    recipient="user@example.com",
    sender="noreply@example.com",
    lang="en",  # Optional: language code
    params={"reset_link": "https://example.com/reset/token"},  # Template variables
    idempotency_key="reset-user-123"  # Optional: prevent duplicates
)
```

### Asynchronous Methods

Async methods use a thread pool executor for non-blocking operation. They return `Future` objects that can be used in various ways:

#### Fire and Forget

Send emails without waiting for responses:

```python
sdk.send_simple_async(
    recipient="user@example.com",
    sender="noreply@example.com",
    subject="Newsletter",
    body="<h1>Latest Updates</h1>"
)
# Continues immediately without blocking
```

#### Using Callbacks

Handle results with callback functions:

```python
def on_complete(success, error):
    if error:
        print(f"Failed to send email: {error}")
    else:
        print("Email sent successfully!")

sdk.send_async(
    tpl="notification",
    recipient="user@example.com",
    sender="noreply@example.com",
    params={"message": "You have a new notification"},
    callback=on_complete
)
```

#### Wait for Results

Send async but wait for completion when needed:

```python
future = sdk.send_simple_async(
    recipient="user@example.com",
    sender="noreply@example.com",
    subject="Confirmation",
    body="<p>Please confirm your action</p>"
)

# Do other work...

# Wait for result (with timeout)
try:
    result = future.result(timeout=10)  # Wait up to 10 seconds
    print(f"Email sent: {result}")
except Exception as e:
    print(f"Email failed: {e}")
```

#### Batch Sending

Send multiple emails concurrently:

```python
recipients = ["user1@example.com", "user2@example.com", "user3@example.com"]
futures = []

for recipient in recipients:
    future = sdk.send_simple_async(
        recipient=recipient,
        sender="noreply@example.com",
        subject="Batch Email",
        body="<p>Hello!</p>",
        idempotency_key=f"batch-{recipient}"
    )
    futures.append(future)

# Wait for all to complete
for future in futures:
    try:
        future.result(timeout=30)
    except Exception as e:
        print(f"Failed: {e}")
```

#### Check Status Without Blocking

```python
future = sdk.send_simple_async(
    recipient="user@example.com",
    sender="noreply@example.com",
    subject="Status Check",
    body="<p>Testing</p>"
)

if future.done():
    result = future.result()
    print(f"Already completed: {result}")
else:
    print("Still processing...")
```

## Configuration

### SDK Options

```python
import logging

sdk = FmailerSdk(
    username="your-domain@example.com",
    password="your-api-token",
    fail_silently=False,  # If True, suppresses exceptions
    max_workers=5,  # Number of concurrent threads for async operations
    log_level=logging.INFO  # Logging level (default: INFO)
)
```

### Logging

The SDK includes comprehensive logging capabilities to help with debugging and monitoring email operations.

#### Log Levels

The SDK supports standard Python logging levels:

- `logging.DEBUG` - Detailed information including request/response data (recommended for development)
- `logging.INFO` - General operational messages about SDK lifecycle and email sends (default)
- `logging.WARNING` - Warning messages
- `logging.ERROR` - Error messages only

#### Basic Logging Configuration

```python
import logging
from fmailersdk.sdk import FmailerSdk

# Enable DEBUG logging to see detailed request/response information
sdk = FmailerSdk(
    username="your-domain@example.com",
    password="your-api-token",
    log_level=logging.DEBUG
)

# Send an email - you'll see detailed logs
sdk.send_simple(
    recipient="user@example.com",
    sender="noreply@example.com",
    subject="Test Email",
    body="<p>Testing with debug logs</p>"
)
```

#### What Gets Logged

**INFO Level:**
- SDK initialization with configuration
- ThreadPoolExecutor creation and shutdown
- Successful email sends

**DEBUG Level:**
- All INFO level messages
- Full request details (URL, parameters, sanitized payload)
- Full response details (status codes, response body)
- Async task lifecycle (submission, start, completion)
- Callback execution

**ERROR Level:**
- API errors (non-2xx responses)
- Network/connection errors
- Async task failures

#### Example Output

```
2025-11-21 17:36:05,170 - fmailersdk.sdk.4472389120 - INFO - FmailerSdk initialized with username=test, max_workers=5, log_level=INFO
2025-11-21 17:36:05,171 - fmailersdk.sdk.4472389120 - INFO - Initializing ThreadPoolExecutor with 5 workers
2025-11-21 17:36:05,171 - fmailersdk.sdk.4472389120 - DEBUG - Sending simple email - URL: https://api.fmailer.ru/external/send_email_simple/, recipient: user@example.com, sender: noreply@example.com, subject: Test, idempotency_key: None
2025-11-21 17:36:05,171 - fmailersdk.sdk.4472389120 - DEBUG - Request payload: {"recipient": "user@example.com", "sender": "noreply@example.com", "subject": "Test", "body": "<p>Test</p>", "auth": "***"}
2025-11-21 17:36:05,171 - fmailersdk.sdk.4472389120 - DEBUG - Response received - status_code: 200, response: {"success": true}
2025-11-21 17:36:05,171 - fmailersdk.sdk.4472389120 - INFO - Simple email sent successfully to user@example.com
```

#### Disable Logging

To disable all logging output:

```python
sdk = FmailerSdk(
    username="your-domain@example.com",
    password="your-api-token",
    log_level=logging.CRITICAL  # Only critical errors
)
```

#### Production Recommendations

For production environments, we recommend:

1. Use `logging.INFO` or `logging.WARNING` to avoid logging sensitive data
2. Configure external log aggregation (e.g., CloudWatch, Datadog)
3. Monitor ERROR level logs for operational issues
4. Use DEBUG level only for troubleshooting specific issues

#### Custom Logging Configuration

If you need more control over logging format or handlers, you can configure Python's logging system before initializing the SDK:

```python
import logging

# Configure global logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fmailer.log'),
        logging.StreamHandler()
    ]
)

# SDK will use the configured logging system
sdk = FmailerSdk(
    username="your-domain@example.com",
    password="your-api-token",
    log_level=logging.DEBUG
)
```

### Cleanup

Properly shutdown the thread pool when done:

```python
# Wait for all pending emails to complete before shutdown
sdk.shutdown(wait=True)
```

Or use a try-finally pattern:

```python
try:
    sdk.send_simple_async(...)
    # ... more operations
finally:
    sdk.shutdown(wait=True)
```

## API Reference

### `FmailerSdk`

#### Constructor

```python
FmailerSdk(username: str, password: str, fail_silently=False, max_workers=5, log_level=logging.INFO)
```

- `username` - Your Fmailer account username (typically your domain)
- `password` - Your Fmailer API token
- `fail_silently` - If True, suppresses exceptions on errors
- `max_workers` - Number of threads for async operations (default: 5)
- `log_level` - Logging level using Python's logging constants (default: logging.INFO). Use logging.DEBUG for detailed request/response logs

#### Methods

##### `send_simple(recipient, sender, subject, body, idempotency_key=None) -> bool`

Send a simple HTML email synchronously.

##### `send(tpl, recipient, sender, lang=None, params=None, idempotency_key=None) -> bool`

Send a templated email synchronously.

##### `send_simple_async(recipient, sender, subject, body, idempotency_key=None, callback=None) -> Future`

Send a simple HTML email asynchronously.

##### `send_async(tpl, recipient, sender, lang=None, params=None, idempotency_key=None, callback=None) -> Future`

Send a templated email asynchronously.

##### `shutdown(wait=True)`

Shutdown the thread pool executor.

### Exceptions

#### `FmailerSdkException`

Raised when API requests fail or network errors occur. Can be suppressed with `fail_silently=True`.

## Development

### Using the Makefile

The project includes a Makefile for common development tasks:

```bash
# View all available commands
make help

# Install dependencies
make install

# Run all tests
make test

# Run synchronous tests only
make test-sync

# Run asynchronous tests only
make test-async

# Run a specific test
make test-specific TEST=tests.FmailersdkAsyncTestUtils.test_send_simple_async_success

# Build the package
make build

# Clean build artifacts
make clean
```

### Testing

The SDK includes a comprehensive test suite covering both synchronous and asynchronous operations.

#### Quick Test Commands (Using Makefile)

```bash
# Run all tests
make test

# Run specific test classes
make test-sync    # Synchronous tests only
make test-async   # Asynchronous tests only

# Run a specific test
make test-specific TEST=tests.FmailersdkAsyncTestUtils.test_send_simple_async_success
```

#### Manual Test Commands (Without Makefile)

```bash
# Run all tests
source .venv/bin/activate
PYTHONPATH=/Users/skyman/Documents/My/Python:$PYTHONPATH python -m unittest tests

# Run specific test class
PYTHONPATH=/Users/skyman/Documents/My/Python:$PYTHONPATH python -m unittest tests.FmailersdkTestUtils

# Run specific test
PYTHONPATH=/Users/skyman/Documents/My/Python:$PYTHONPATH python -m unittest tests.FmailersdkAsyncTestUtils.test_send_simple_async_success
```

### Building and Publishing

Build the package for distribution:

```bash
# Build the package
make build

# Publish to TestPyPI (for testing)
make publish-test

# Publish to PyPI (production)
make publish
```

Or manually:

```bash
# Build
python -m build

# Check the distribution
twine check dist/*

# Upload to PyPI
twine upload dist/*
```

## Examples

See `async_example.py` for comprehensive examples of all async patterns including:
- Fire and forget
- Callback handling
- Waiting for results
- Batch sending
- Status checking
- Proper cleanup

## API Endpoints

The SDK communicates with the following Fmailer API endpoints:

- **Base URL**: `https://api.fmailer.ru/external/`
- **Simple Send**: `POST /external/send_email_simple/`
- **Template Send**: `POST /external/send_email_tpl/`

## Contributing

Contributions are welcome! Please ensure all tests pass before submitting a pull request.

## License

[Add your license information here]

## Support

For issues, questions, or feature requests, please contact Fmailer support or open an issue in this repository.
