"""FmailerSDK - Python SDK for Fmailer email service API."""

from .sdk import FmailerSdk
from .exceptions import FmailerSdkException

__version__ = "1.0.0"
__all__ = ["FmailerSdk", "FmailerSdkException"]
