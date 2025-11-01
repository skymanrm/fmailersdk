import logging
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Callable

import requests
from requests import exceptions
import json

from .exceptions import FmailerSdkException


logger = logging.getLogger(__name__)


class FmailerSdk:
    SERVER_URL = "https://api.fmailer.ru"
    auth = {}
    fail_silently = False
    debug = False
    _executor = None
    _max_workers = 5

    @property
    def api_url(self):
        return f"{self.SERVER_URL}/external/"

    @property
    def executor(self) -> ThreadPoolExecutor:
        """Lazy initialization of thread pool executor"""
        if self._executor is None:
            self._executor = ThreadPoolExecutor(max_workers=self._max_workers)
        return self._executor

    def __init__(self, username: str, password: str, fail_silently=False, max_workers=5):
        self.auth = {"username": username, "password": password}
        self.fail_silently = fail_silently
        self._max_workers = max_workers

    def send_simple(
        self,
        recipient: str,
        sender: str,
        subject: str,
        body: str,
        idempotency_key: str = None,
    ) -> bool:
        payload = {
            "auth": self.auth,
            "recipient": recipient,
            "sender": sender,
            "subject": subject,
            "body": body,
            "idempotency_key": idempotency_key,
        }
        try:
            path = f"{self.api_url}send_email_simple/"
            res = requests.post(path, json=payload)
            if not res.ok:
                raise FmailerSdkException(res.text)
        except exceptions.RequestException as exc:
            if not self.fail_silently:
                raise FmailerSdkException("Fmailer API error") from exc
        return True

    def send(
        self,
        tpl: str,
        recipient: str,
        sender: str,
        lang: str | None = None,
        params: dict | None = None,
        idempotency_key: str | None = None,
    ):
        payload = {
            "auth": self.auth,
            "tpl": tpl,
            "recipient": recipient,
            "sender": sender,
            "lang": lang,
            "params": params,
            "idempotency_key": idempotency_key,
        }
        try:
            path = f"{self.api_url}send_email_tpl/"
            if self.debug:
                logger.info(f"New email, path={path}, payload={json.dumps(payload)}")
            res = requests.post(path, json=payload)
            logger.info(f"Result, status_code={res.status_code}, res={res.text}")
            if not res.ok:
                raise FmailerSdkException(str(res.text))
        except exceptions.RequestException as exc:
            if not self.fail_silently:
                raise FmailerSdkException("Fmailer API error") from exc
        return True

    def send_simple_async(
        self,
        recipient: str,
        sender: str,
        subject: str,
        body: str,
        idempotency_key: str = None,
        callback: Callable[[bool, Exception | None], None] | None = None,
    ) -> Future:
        """
        Send a simple email asynchronously in a background thread.

        Args:
            recipient: Email recipient
            sender: Email sender
            subject: Email subject
            body: Email body (HTML)
            idempotency_key: Optional unique key to prevent duplicate sends
            callback: Optional callback function called with (result, exception)

        Returns:
            Future object that can be used to wait for the result or check status

        Example:
            # Fire and forget
            sdk.send_simple_async(recipient="user@example.com", ...)

            # With callback
            def on_complete(success, error):
                if error:
                    print(f"Error: {error}")
                else:
                    print("Email sent successfully")

            sdk.send_simple_async(recipient="user@example.com", ..., callback=on_complete)

            # Wait for result
            future = sdk.send_simple_async(recipient="user@example.com", ...)
            result = future.result()  # Blocks until complete
        """
        def task():
            try:
                result = self.send_simple(
                    recipient=recipient,
                    sender=sender,
                    subject=subject,
                    body=body,
                    idempotency_key=idempotency_key,
                )
                if callback:
                    callback(result, None)
                return result
            except Exception as e:
                if callback:
                    callback(False, e)
                raise

        return self.executor.submit(task)

    def send_async(
        self,
        tpl: str,
        recipient: str,
        sender: str,
        lang: str | None = None,
        params: dict | None = None,
        idempotency_key: str | None = None,
        callback: Callable[[bool, Exception | None], None] | None = None,
    ) -> Future:
        """
        Send a templated email asynchronously in a background thread.

        Args:
            tpl: Template name
            recipient: Email recipient
            sender: Email sender
            lang: Language code (e.g., 'en', 'ru')
            params: Template parameters
            idempotency_key: Optional unique key to prevent duplicate sends
            callback: Optional callback function called with (result, exception)

        Returns:
            Future object that can be used to wait for the result or check status

        Example:
            # Fire and forget
            sdk.send_async(tpl="welcome", recipient="user@example.com", ...)

            # With callback
            def on_complete(success, error):
                if error:
                    print(f"Error: {error}")
                else:
                    print("Email sent successfully")

            sdk.send_async(tpl="welcome", ..., callback=on_complete)

            # Wait for result
            future = sdk.send_async(tpl="welcome", ...)
            result = future.result()  # Blocks until complete
        """
        def task():
            try:
                result = self.send(
                    tpl=tpl,
                    recipient=recipient,
                    sender=sender,
                    lang=lang,
                    params=params,
                    idempotency_key=idempotency_key,
                )
                if callback:
                    callback(result, None)
                return result
            except Exception as e:
                if callback:
                    callback(False, e)
                raise

        return self.executor.submit(task)

    def shutdown(self, wait=True):
        """
        Shutdown the thread pool executor.

        Args:
            wait: If True, wait for all pending tasks to complete
        """
        if self._executor is not None:
            self._executor.shutdown(wait=wait)
            self._executor = None

    def __del__(self):
        """Cleanup executor on garbage collection"""
        self.shutdown(wait=False)
