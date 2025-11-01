"""
Example usage of FmailerSDK async methods.

The SDK now supports asynchronous email sending using background threads,
allowing the main thread to continue without waiting for API responses.
"""

from .sdk import FmailerSdk


# Initialize SDK
sdk = FmailerSdk(
    username="your-domain@example.com",
    password="your-token",
    max_workers=10  # Number of concurrent background threads
)


# Example 1: Fire and forget - don't wait for response
def fire_and_forget_example():
    """Send email without waiting for response"""
    sdk.send_simple_async(
        recipient="user@example.com",
        sender="noreply@example.com",
        subject="Welcome!",
        body="<h1>Hello World</h1>",
        idempotency_key="unique-key-1"
    )
    print("Email queued, continuing with other work...")
    # Main thread continues immediately


# Example 2: Using callbacks
def callback_example():
    """Send email with callback when complete"""

    def on_email_sent(success, error):
        if error:
            print(f"Email failed: {error}")
        else:
            print("Email sent successfully!")

    sdk.send_async(
        tpl="welcome-email",
        recipient="user@example.com",
        sender="noreply@example.com",
        lang="en",
        params={"name": "John", "code": "123456"},
        callback=on_email_sent
    )
    print("Email queued, callback will be called when complete...")


# Example 3: Wait for result when needed
def wait_for_result_example():
    """Send email and wait for result"""

    future = sdk.send_simple_async(
        recipient="user@example.com",
        sender="noreply@example.com",
        subject="Important",
        body="<p>This is important</p>",
    )

    print("Email queued, doing other work...")
    # Do other work here...

    # Wait for result when you need it
    try:
        result = future.result(timeout=10)  # Wait up to 10 seconds
        print(f"Email sent: {result}")
    except Exception as e:
        print(f"Email failed: {e}")


# Example 4: Send multiple emails in parallel
def batch_send_example():
    """Send multiple emails concurrently"""

    recipients = [
        "user1@example.com",
        "user2@example.com",
        "user3@example.com",
    ]

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

    print(f"Queued {len(futures)} emails, waiting for completion...")

    # Wait for all to complete
    for i, future in enumerate(futures):
        try:
            result = future.result(timeout=30)
            print(f"Email {i+1} sent: {result}")
        except Exception as e:
            print(f"Email {i+1} failed: {e}")


# Example 5: Check status without blocking
def check_status_example():
    """Send email and check status without blocking"""

    future = sdk.send_simple_async(
        recipient="user@example.com",
        sender="noreply@example.com",
        subject="Status Check",
        body="<p>Testing status</p>",
    )

    # Check if done without blocking
    if future.done():
        print("Email already sent")
        try:
            result = future.result()
            print(f"Result: {result}")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("Email still sending...")
        # You can check again later or wait for it
        future.result()  # This will block until complete


# Example 6: Proper cleanup
def cleanup_example():
    """Properly shutdown SDK when done"""

    # Send some emails
    sdk.send_simple_async(
        recipient="user@example.com",
        sender="noreply@example.com",
        subject="Test",
        body="<p>Test</p>",
    )

    # When you're done with the SDK, shutdown the thread pool
    # wait=True ensures all pending emails are sent before shutdown
    sdk.shutdown(wait=True)
    print("All emails sent, executor shutdown")


# Example 7: Context manager style (if needed)
def context_manager_style():
    """Using SDK in a controlled scope"""

    sdk_instance = FmailerSdk(
        username="your-domain@example.com",
        password="your-token"
    )

    try:
        # Send emails
        sdk_instance.send_simple_async(
            recipient="user@example.com",
            sender="noreply@example.com",
            subject="Test",
            body="<p>Test</p>",
        )
    finally:
        # Ensure cleanup
        sdk_instance.shutdown(wait=True)


if __name__ == "__main__":
    print("FmailerSDK Async Usage Examples")
    print("=" * 50)

    # Uncomment to run examples:
    # fire_and_forget_example()
    # callback_example()
    # wait_for_result_example()
    # batch_send_example()
    # check_status_example()
    # cleanup_example()
