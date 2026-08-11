import logging
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Callable

import requests
from requests import exceptions
import json

from .exceptions import PostwingSdkException


logger = logging.getLogger(__name__)


class PostwingSdk:
    SERVER_URL = "https://api.postwing.app"
    auth = {}
    fail_silently = False
    debug = False
    _executor = None
    _max_workers = 5
    _logger = None

    @property
    def api_url(self):
        return f"{self.SERVER_URL}/external/"

    @property
    def executor(self) -> ThreadPoolExecutor:
        """Lazy initialization of thread pool executor"""
        if self._executor is None:
            self._logger.info(f"Initializing ThreadPoolExecutor with {self._max_workers} workers")
            self._executor = ThreadPoolExecutor(max_workers=self._max_workers)
        return self._executor

    def __init__(self, username: str, password: str, fail_silently=False, max_workers=5, log_level=logging.INFO):
        """
        Initialize PostwingSdk.

        Args:
            username: API username
            password: API password
            fail_silently: If True, suppress exceptions and return False on errors
            max_workers: Number of worker threads for async operations
            log_level: Logging level (e.g., logging.DEBUG, logging.INFO, logging.WARNING)
                      Use logging.DEBUG to see detailed request/response logs
        """
        self.auth = {"username": username, "password": password}
        self.fail_silently = fail_silently
        self._max_workers = max_workers

        # Configure logger for this instance
        self._logger = logging.getLogger(f"{__name__}.{id(self)}")
        self._logger.setLevel(log_level)

        # Add handler if none exists (avoid duplicate handlers)
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            handler.setLevel(log_level)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)

        self._logger.info(f"PostwingSdk initialized with username={username}, max_workers={max_workers}, log_level={logging.getLevelName(log_level)}")

    def send_simple(
        self,
        recipient: str,
        sender: str,
        subject: str,
        body: str,
        idempotency_key: str = None,
        reply_to: str = None,
        headers: dict = None,
        text: str = None,
        mass_mail: bool = None,
    ) -> bool:
        """Send a ready-made message.

        Args:
            body: the HTML part.
            text: the plain-text part. Optional — omitted, the API derives one
                from `body`. Worth sending: a derived part cannot know which
                parts of a layout were decoration, and every message carries
                both parts either way.
            mass_mail: True for marketing and other bulk mail. Attaches the
                one-click unsubscribe headers Apple, Gmail and Yahoo require of
                bulk senders. One-way — False does not remove them, it leaves
                the decision to the API's own classifier.
        """
        payload = {
            "auth": self.auth,
            "recipient": recipient,
            "sender": sender,
            "subject": subject,
            "body": body,
            "idempotency_key": idempotency_key,
        }
        # Only sent when set, so this client keeps working against an API
        # deployment that predates these fields and would reject them.
        if reply_to is not None:
            payload["reply_to"] = reply_to
        if headers:
            payload["headers"] = headers
        if text is not None:
            payload["text"] = text
        if mass_mail is not None:
            payload["mass_mail"] = mass_mail
        try:
            path = f"{self.api_url}send_email_simple/"

            # Debug log for request
            self._logger.debug(
                f"Sending simple email - URL: {path}, "
                f"recipient: {recipient}, sender: {sender}, subject: {subject}, "
                f"idempotency_key: {idempotency_key}"
            )
            self._logger.debug(f"Request payload: {json.dumps({**payload, 'auth': '***'}, default=str)}")

            res = requests.post(
                path,
                data=json.dumps(payload, default=str),
                headers={"Content-Type": "application/json"},
                timeout=5,
            )

            # Debug log for response
            try:
                response_text = res.text[:200] + "..." if len(res.text) > 200 else res.text
            except (TypeError, AttributeError):
                response_text = str(res.text)
            self._logger.debug(f"Response received - status_code: {res.status_code}, response: {response_text}")

            if not res.ok:
                self._logger.error(f"API error - status: {res.status_code}, response: {res.text}")
                raise PostwingSdkException(res.text)

            self._logger.info(f"Simple email sent successfully to {recipient}")
        except exceptions.RequestException as exc:
            self._logger.error(f"Request exception while sending email: {exc}")
            if not self.fail_silently:
                raise PostwingSdkException("Postwing API error") from exc
        return True

    def send(
        self,
        tpl: str,
        recipient: str,
        sender: str,
        lang: str | None = None,
        params: dict | None = None,
        idempotency_key: str | None = None,
        reply_to: str | None = None,
        headers: dict | None = None,
        text: str | None = None,
        mass_mail: bool | None = None,
    ):
        """Render a saved template and send it.

        Args:
            text: the plain-text part. Note that it is used **verbatim** — a
                template's `params` are substituted into the template's own
                body, never into this string, so a `text` here should not
                contain placeholders. Omit it and the API derives one from the
                rendered HTML, with the substitutions already applied.
            mass_mail: True for bulk mail; see `send_simple`.
        """
        payload = {
            "auth": self.auth,
            "tpl": tpl,
            "recipient": recipient,
            "sender": sender,
            "lang": lang,
            "params": params,
            "idempotency_key": idempotency_key,
        }
        # Only sent when set — see send_simple.
        if reply_to is not None:
            payload["reply_to"] = reply_to
        if headers:
            payload["headers"] = headers
        if text is not None:
            payload["text"] = text
        if mass_mail is not None:
            payload["mass_mail"] = mass_mail
        try:
            path = f"{self.api_url}send_email_tpl/"

            # Debug log for request
            self._logger.debug(
                f"Sending templated email - URL: {path}, "
                f"template: {tpl}, recipient: {recipient}, sender: {sender}, "
                f"lang: {lang}, idempotency_key: {idempotency_key}"
            )
            self._logger.debug(f"Request payload: {json.dumps({**payload, 'auth': '***'}, default=str)}")

            res = requests.post(
                path,
                data=json.dumps(payload, default=str),
                headers={"Content-Type": "application/json"},
                timeout=5,
            )

            # Debug log for response
            try:
                response_text = res.text[:200] + "..." if len(res.text) > 200 else res.text
            except (TypeError, AttributeError):
                response_text = str(res.text)
            self._logger.debug(f"Response received - status_code: {res.status_code}, response: {response_text}")

            if not res.ok:
                self._logger.error(f"API error - status: {res.status_code}, response: {res.text}")
                raise PostwingSdkException(str(res.text))

            self._logger.info(f"Templated email sent successfully to {recipient} using template '{tpl}'")
        except exceptions.RequestException as exc:
            self._logger.error(f"Request exception while sending email: {exc}")
            if not self.fail_silently:
                raise PostwingSdkException("Postwing API error") from exc
        return True

    def send_simple_async(
        self,
        recipient: str,
        sender: str,
        subject: str,
        body: str,
        idempotency_key: str = None,
        reply_to: str = None,
        headers: dict = None,
        text: str = None,
        mass_mail: bool = None,
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
            reply_to: Optional address replies should go to (Reply-To header)
            headers: Optional extra headers. The API allowlists these:
                In-Reply-To, References, Reply-To, and any X-* header.
            text: Optional plain-text part. Omitted, the API derives one from
                the HTML body.
            mass_mail: True for bulk mail — attaches the one-click unsubscribe
                headers. One-way; see send_simple.
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
        self._logger.debug(f"Submitting async simple email task for {recipient}")

        def task():
            try:
                self._logger.debug(f"Async task started for simple email to {recipient}")
                result = self.send_simple(
                    recipient=recipient,
                    sender=sender,
                    subject=subject,
                    body=body,
                    idempotency_key=idempotency_key,
                    reply_to=reply_to,
                    headers=headers,
                    text=text,
                    mass_mail=mass_mail,
                )
                if callback:
                    self._logger.debug(f"Calling callback for successful async email to {recipient}")
                    callback(result, None)
                self._logger.debug(f"Async task completed successfully for {recipient}")
                return result
            except Exception as e:
                self._logger.error(f"Async task failed for {recipient}: {e}")
                if callback:
                    self._logger.debug(f"Calling callback with error for {recipient}")
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
        reply_to: str | None = None,
        headers: dict | None = None,
        text: str | None = None,
        mass_mail: bool | None = None,
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
            reply_to: Optional address replies should go to (Reply-To header)
            headers: Optional extra headers. The API allowlists these:
                In-Reply-To, References, Reply-To, and any X-* header.
            text: Optional plain-text part, used verbatim — `params` are not
                substituted into it; see send().
            mass_mail: True for bulk mail — attaches the one-click unsubscribe
                headers. One-way; see send_simple.
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
        self._logger.debug(f"Submitting async templated email task for {recipient} with template '{tpl}'")

        def task():
            try:
                self._logger.debug(f"Async task started for templated email to {recipient} (template: {tpl})")
                result = self.send(
                    tpl=tpl,
                    recipient=recipient,
                    sender=sender,
                    lang=lang,
                    params=params,
                    idempotency_key=idempotency_key,
                    reply_to=reply_to,
                    headers=headers,
                    text=text,
                    mass_mail=mass_mail,
                )
                if callback:
                    self._logger.debug(f"Calling callback for successful async email to {recipient}")
                    callback(result, None)
                self._logger.debug(f"Async task completed successfully for {recipient}")
                return result
            except Exception as e:
                self._logger.error(f"Async task failed for {recipient}: {e}")
                if callback:
                    self._logger.debug(f"Calling callback with error for {recipient}")
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
            self._logger.info(f"Shutting down ThreadPoolExecutor (wait={wait})")
            self._executor.shutdown(wait=wait)
            self._executor = None
            self._logger.debug("ThreadPoolExecutor shutdown complete")

    def __del__(self):
        """Cleanup executor on garbage collection"""
        if self._logger:
            self._logger.debug("PostwingSdk instance being destroyed, cleaning up executor")
        self.shutdown(wait=False)
