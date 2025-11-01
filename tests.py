import unittest
from unittest.mock import patch, Mock, MagicMock
import time
from concurrent.futures import TimeoutError as FuturesTimeoutError

import requests
from faker import Faker

from exceptions import FmailerSdkException
from sdk import FmailerSdk

faker = Faker()


class FmailersdkTestUtils(unittest.TestCase):
    @patch("requests.post")
    def test_send_simple_exception(self, mock_post):
        mock_post.side_effect = requests.exceptions.ConnectionError()
        sdk = FmailerSdk("test", "test")
        with self.assertRaises(FmailerSdkException) as context:
            res = sdk.send("test", faker.email(), faker.email(), "ru", {}, "")
        self.assertTrue("Fmailer" in str(context.exception))

    @patch("requests.post")
    def test_send_simple_exception_400(self, mock_post):
        mock_post.return_value.status_code = 400
        mock_post.return_value.ok = False
        mock_post.return_value.text = {"err": "error"}
        sdk = FmailerSdk("test", "test")
        with self.assertRaises(FmailerSdkException) as context:
            res = sdk.send("test", faker.email(), faker.email(), "ru", {}, "")
        self.assertIn("err", str(context.exception))


class FmailersdkAsyncTestUtils(unittest.TestCase):
    """Tests for async SDK methods"""

    def tearDown(self):
        """Cleanup after each test"""
        # Clean up any SDK instances
        if hasattr(self, 'sdk') and self.sdk:
            self.sdk.shutdown(wait=True)

    @patch("requests.post")
    def test_send_simple_async_success(self, mock_post):
        """Test send_simple_async returns a Future and completes successfully"""
        mock_post.return_value.ok = True
        mock_post.return_value.status_code = 200

        sdk = FmailerSdk("test", "test")
        self.sdk = sdk

        future = sdk.send_simple_async(
            recipient=faker.email(),
            sender=faker.email(),
            subject="Test Subject",
            body="<p>Test Body</p>",
            idempotency_key="test-key"
        )

        # Verify it returns a Future
        self.assertIsNotNone(future)

        # Wait for result
        result = future.result(timeout=5)

        # Verify result
        self.assertTrue(result)
        mock_post.assert_called_once()

    @patch("requests.post")
    def test_send_async_success(self, mock_post):
        """Test send_async returns a Future and completes successfully"""
        mock_post.return_value.ok = True
        mock_post.return_value.status_code = 200
        mock_post.return_value.text = "OK"

        sdk = FmailerSdk("test", "test")
        self.sdk = sdk

        future = sdk.send_async(
            tpl="welcome",
            recipient=faker.email(),
            sender=faker.email(),
            lang="en",
            params={"name": "John"},
            idempotency_key="test-key"
        )

        # Verify it returns a Future
        self.assertIsNotNone(future)

        # Wait for result
        result = future.result(timeout=5)

        # Verify result
        self.assertTrue(result)
        mock_post.assert_called_once()

    @patch("requests.post")
    def test_send_simple_async_with_callback_success(self, mock_post):
        """Test send_simple_async callback is called on success"""
        mock_post.return_value.ok = True
        mock_post.return_value.status_code = 200

        sdk = FmailerSdk("test", "test")
        self.sdk = sdk

        # Create callback mock
        callback = Mock()

        future = sdk.send_simple_async(
            recipient=faker.email(),
            sender=faker.email(),
            subject="Test",
            body="<p>Test</p>",
            callback=callback
        )

        # Wait for completion
        future.result(timeout=5)

        # Verify callback was called with success
        callback.assert_called_once()
        args = callback.call_args[0]
        self.assertTrue(args[0])  # result should be True
        self.assertIsNone(args[1])  # error should be None

    @patch("requests.post")
    def test_send_async_with_callback_success(self, mock_post):
        """Test send_async callback is called on success"""
        mock_post.return_value.ok = True
        mock_post.return_value.status_code = 200
        mock_post.return_value.text = "OK"

        sdk = FmailerSdk("test", "test")
        self.sdk = sdk

        # Create callback mock
        callback = Mock()

        future = sdk.send_async(
            tpl="test",
            recipient=faker.email(),
            sender=faker.email(),
            callback=callback
        )

        # Wait for completion
        future.result(timeout=5)

        # Verify callback was called with success
        callback.assert_called_once()
        args = callback.call_args[0]
        self.assertTrue(args[0])  # result should be True
        self.assertIsNone(args[1])  # error should be None

    @patch("requests.post")
    def test_send_simple_async_with_callback_error(self, mock_post):
        """Test send_simple_async callback is called on error"""
        mock_post.side_effect = requests.exceptions.ConnectionError()

        sdk = FmailerSdk("test", "test")
        self.sdk = sdk

        # Create callback mock
        callback = Mock()

        future = sdk.send_simple_async(
            recipient=faker.email(),
            sender=faker.email(),
            subject="Test",
            body="<p>Test</p>",
            callback=callback
        )

        # Wait for completion and expect exception
        with self.assertRaises(FmailerSdkException):
            future.result(timeout=5)

        # Verify callback was called with error
        callback.assert_called_once()
        args = callback.call_args[0]
        self.assertFalse(args[0])  # result should be False
        self.assertIsNotNone(args[1])  # error should be present
        self.assertIsInstance(args[1], FmailerSdkException)

    @patch("requests.post")
    def test_send_async_with_callback_error(self, mock_post):
        """Test send_async callback is called on error"""
        mock_post.return_value.ok = False
        mock_post.return_value.status_code = 400
        mock_post.return_value.text = "Bad Request"

        sdk = FmailerSdk("test", "test")
        self.sdk = sdk

        # Create callback mock
        callback = Mock()

        future = sdk.send_async(
            tpl="test",
            recipient=faker.email(),
            sender=faker.email(),
            callback=callback
        )

        # Wait for completion and expect exception
        with self.assertRaises(FmailerSdkException):
            future.result(timeout=5)

        # Verify callback was called with error
        callback.assert_called_once()
        args = callback.call_args[0]
        self.assertFalse(args[0])  # result should be False
        self.assertIsNotNone(args[1])  # error should be present

    @patch("requests.post")
    def test_send_simple_async_exception(self, mock_post):
        """Test send_simple_async propagates exceptions"""
        mock_post.side_effect = requests.exceptions.ConnectionError()

        sdk = FmailerSdk("test", "test")
        self.sdk = sdk

        future = sdk.send_simple_async(
            recipient=faker.email(),
            sender=faker.email(),
            subject="Test",
            body="<p>Test</p>"
        )

        # Should raise exception when getting result
        with self.assertRaises(FmailerSdkException):
            future.result(timeout=5)

    @patch("requests.post")
    def test_send_async_exception(self, mock_post):
        """Test send_async propagates exceptions"""
        mock_post.return_value.ok = False
        mock_post.return_value.status_code = 500
        mock_post.return_value.text = "Internal Server Error"

        sdk = FmailerSdk("test", "test")
        self.sdk = sdk

        future = sdk.send_async(
            tpl="test",
            recipient=faker.email(),
            sender=faker.email()
        )

        # Should raise exception when getting result
        with self.assertRaises(FmailerSdkException):
            future.result(timeout=5)

    @patch("requests.post")
    def test_multiple_async_requests_concurrent(self, mock_post):
        """Test multiple async requests execute concurrently"""
        mock_post.return_value.ok = True
        mock_post.return_value.status_code = 200

        sdk = FmailerSdk("test", "test", max_workers=3)
        self.sdk = sdk

        # Send multiple emails
        futures = []
        for i in range(5):
            future = sdk.send_simple_async(
                recipient=faker.email(),
                sender=faker.email(),
                subject=f"Test {i}",
                body="<p>Test</p>",
                idempotency_key=f"key-{i}"
            )
            futures.append(future)

        # Wait for all to complete
        results = [f.result(timeout=5) for f in futures]

        # Verify all succeeded
        self.assertEqual(len(results), 5)
        self.assertTrue(all(results))
        self.assertEqual(mock_post.call_count, 5)

    @patch("requests.post")
    def test_future_done_method(self, mock_post):
        """Test Future.done() method works correctly"""
        # Simulate slow request
        def slow_response(*args, **kwargs):
            time.sleep(0.1)
            response = Mock()
            response.ok = True
            response.status_code = 200
            return response

        mock_post.side_effect = slow_response

        sdk = FmailerSdk("test", "test")
        self.sdk = sdk

        future = sdk.send_simple_async(
            recipient=faker.email(),
            sender=faker.email(),
            subject="Test",
            body="<p>Test</p>"
        )

        # Should not be done immediately
        self.assertFalse(future.done())

        # Wait for completion
        future.result(timeout=5)

        # Should be done now
        self.assertTrue(future.done())

    @patch("requests.post")
    def test_executor_initialization(self, mock_post):
        """Test executor is lazily initialized"""
        sdk = FmailerSdk("test", "test", max_workers=10)
        self.sdk = sdk

        # Executor should not be created yet
        self.assertIsNone(sdk._executor)

        # Make a request
        mock_post.return_value.ok = True
        mock_post.return_value.status_code = 200

        future = sdk.send_simple_async(
            recipient=faker.email(),
            sender=faker.email(),
            subject="Test",
            body="<p>Test</p>"
        )

        # Now executor should exist
        self.assertIsNotNone(sdk._executor)

        # Wait for completion
        future.result(timeout=5)

    @patch("requests.post")
    def test_shutdown_waits_for_completion(self, mock_post):
        """Test shutdown waits for pending tasks"""
        def slow_response(*args, **kwargs):
            time.sleep(0.2)
            response = Mock()
            response.ok = True
            response.status_code = 200
            return response

        mock_post.side_effect = slow_response

        sdk = FmailerSdk("test", "test")

        # Start async request
        future = sdk.send_simple_async(
            recipient=faker.email(),
            sender=faker.email(),
            subject="Test",
            body="<p>Test</p>"
        )

        # Shutdown with wait=True should wait for completion
        start_time = time.time()
        sdk.shutdown(wait=True)
        elapsed = time.time() - start_time

        # Should have waited at least 0.2 seconds
        self.assertGreaterEqual(elapsed, 0.2)

        # Task should be done
        self.assertTrue(future.done())

    @patch("requests.post")
    def test_shutdown_without_wait(self, mock_post):
        """Test shutdown without waiting for completion"""
        def slow_response(*args, **kwargs):
            time.sleep(0.5)
            response = Mock()
            response.ok = True
            response.status_code = 200
            return response

        mock_post.side_effect = slow_response

        sdk = FmailerSdk("test", "test")

        # Start async request
        future = sdk.send_simple_async(
            recipient=faker.email(),
            sender=faker.email(),
            subject="Test",
            body="<p>Test</p>"
        )

        # Shutdown with wait=False should return immediately
        start_time = time.time()
        sdk.shutdown(wait=False)
        elapsed = time.time() - start_time

        # Should return quickly (less than 0.1 seconds)
        self.assertLess(elapsed, 0.1)

    @patch("requests.post")
    def test_fail_silently_async(self, mock_post):
        """Test fail_silently works with async methods"""
        mock_post.side_effect = requests.exceptions.ConnectionError()

        sdk = FmailerSdk("test", "test", fail_silently=True)
        self.sdk = sdk

        future = sdk.send_simple_async(
            recipient=faker.email(),
            sender=faker.email(),
            subject="Test",
            body="<p>Test</p>"
        )

        # Should not raise exception due to fail_silently
        result = future.result(timeout=5)
        self.assertTrue(result)

    @patch("requests.post")
    def test_async_methods_preserve_sync_behavior(self, mock_post):
        """Test that async methods call the sync methods correctly"""
        mock_post.return_value.ok = True
        mock_post.return_value.status_code = 200
        mock_post.return_value.text = "OK"

        sdk = FmailerSdk("test", "test")
        self.sdk = sdk

        recipient = faker.email()
        sender = faker.email()

        # Call async method
        future = sdk.send_simple_async(
            recipient=recipient,
            sender=sender,
            subject="Test Subject",
            body="<p>Test Body</p>",
            idempotency_key="test-key"
        )

        future.result(timeout=5)

        # Verify the underlying requests.post was called with correct data
        self.assertEqual(mock_post.call_count, 1)
        call_kwargs = mock_post.call_args[1]
        payload = call_kwargs['json']

        self.assertEqual(payload['recipient'], recipient)
        self.assertEqual(payload['sender'], sender)
        self.assertEqual(payload['subject'], "Test Subject")
        self.assertEqual(payload['body'], "<p>Test Body</p>")
        self.assertEqual(payload['idempotency_key'], "test-key")
