"""Browser automation module."""

from .driver import BrowserDriver
from .actions import BrowserActions
from .observer import PageObserver

__all__ = ["BrowserDriver", "BrowserActions", "PageObserver"]
