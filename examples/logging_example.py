"""
Example demonstrating FmailerSDK logging capabilities.

This example shows how to configure different log levels and what information
is logged at each level.
"""

import logging
from fmailersdk.sdk import FmailerSdk

def example_info_logging():
    """Example with INFO level logging (default)"""
    print("\n=== Example 1: INFO Level Logging (default) ===\n")

    sdk = FmailerSdk(
        username="test@example.com",
        password="test-token",
        log_level=logging.INFO
    )

    print("INFO level shows:")
    print("- SDK initialization")
    print("- Executor creation")
    print("- Successful email sends")
    print("- Error messages\n")

    # Note: This example uses fake credentials, so it would fail in real usage
    # In production, replace with actual credentials

    sdk.shutdown()


def example_debug_logging():
    """Example with DEBUG level logging"""
    print("\n=== Example 2: DEBUG Level Logging ===\n")

    sdk = FmailerSdk(
        username="test@example.com",
        password="test-token",
        log_level=logging.DEBUG
    )

    print("DEBUG level shows:")
    print("- All INFO level logs")
    print("- Full request details (URL, parameters)")
    print("- Sanitized payload (auth credentials hidden)")
    print("- Response status codes and body")
    print("- Async task lifecycle")
    print("- Callback execution\n")

    sdk.shutdown()


def example_error_only_logging():
    """Example with ERROR level logging (minimal output)"""
    print("\n=== Example 3: ERROR Level Logging (minimal) ===\n")

    sdk = FmailerSdk(
        username="test@example.com",
        password="test-token",
        log_level=logging.ERROR
    )

    print("ERROR level shows:")
    print("- Only error messages")
    print("- No informational or debug output\n")

    sdk.shutdown()


def example_custom_logging():
    """Example with custom logging configuration"""
    print("\n=== Example 4: Custom Logging Configuration ===\n")

    # Configure logging to write to file and console
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('fmailer_debug.log'),
            logging.StreamHandler()
        ]
    )

    sdk = FmailerSdk(
        username="test@example.com",
        password="test-token",
        log_level=logging.DEBUG
    )

    print("Custom configuration:")
    print("- Logs written to both file and console")
    print("- Custom format with timestamps")
    print("- File: fmailer_debug.log\n")

    sdk.shutdown()


def example_production_config():
    """Example of recommended production configuration"""
    print("\n=== Example 5: Production Configuration ===\n")

    # Production: INFO level with file logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('fmailer_production.log')
        ]
    )

    sdk = FmailerSdk(
        username="test@example.com",
        password="test-token",
        log_level=logging.INFO,
        fail_silently=True  # Don't raise exceptions in production
    )

    print("Production recommendations:")
    print("- Use INFO or WARNING level")
    print("- Log to file or external system (CloudWatch, Datadog)")
    print("- Enable fail_silently for graceful degradation")
    print("- Monitor ERROR level logs for issues")
    print("- Only use DEBUG for troubleshooting\n")

    sdk.shutdown()


if __name__ == "__main__":
    print("FmailerSDK Logging Examples")
    print("=" * 60)

    example_info_logging()
    example_debug_logging()
    example_error_only_logging()
    example_custom_logging()
    example_production_config()

    print("\n" + "=" * 60)
    print("Examples complete!")
    print("\nTo actually send emails, replace the credentials with your")
    print("real Fmailer API credentials and call send_simple() or send()")
