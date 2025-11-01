# FmailerSDK

A Python SDK for the [Fmailer](https://api.fmailer.ru) email service API. Provides both synchronous and asynchronous methods for sending emails via templates or simple HTML content.

## Features

- **Synchronous and Asynchronous API** - Choose between blocking and non-blocking email sending
- **Template Support** - Send emails using pre-configured templates with parameters
- **Simple HTML Emails** - Send plain HTML emails directly
- **Idempotency Keys** - Prevent duplicate email sends with unique keys
- **Multi-language Support** - Send templated emails in different languages
- **Thread Pool Execution** - Efficient concurrent email sending with configurable worker threads
- **Callback Support** - Handle async results with callbacks for fire-and-forget patterns
- **Fail Silently Mode** - Option to suppress exceptions for graceful degradation

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
sdk = FmailerSdk(
    username="your-domain@example.com",
    password="your-api-token",
    fail_silently=False,  # If True, suppresses exceptions
    max_workers=5  # Number of concurrent threads for async operations
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
FmailerSdk(username: str, password: str, fail_silently=False, max_workers=5)
```

- `username` - Your Fmailer account username (typically your domain)
- `password` - Your Fmailer API token
- `fail_silently` - If True, suppresses exceptions on errors
- `max_workers` - Number of threads for async operations (default: 5)

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

## Testing

The SDK includes a comprehensive test suite covering both synchronous and asynchronous operations.

### Run All Tests

```bash
source .venv/bin/activate
PYTHONPATH=/Users/skyman/Documents/My/Python:$PYTHONPATH python -m unittest tests
```

### Run Specific Test Class

```bash
# Synchronous tests
PYTHONPATH=/Users/skyman/Documents/My/Python:$PYTHONPATH python -m unittest tests.FmailersdkTestUtils

# Asynchronous tests
PYTHONPATH=/Users/skyman/Documents/My/Python:$PYTHONPATH python -m unittest tests.FmailersdkAsyncTestUtils
```

### Run Specific Test

```bash
PYTHONPATH=/Users/skyman/Documents/My/Python:$PYTHONPATH python -m unittest tests.FmailersdkAsyncTestUtils.test_send_simple_async_success
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
