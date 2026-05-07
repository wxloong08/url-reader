"""
Fetch strategies for URL Reader.
Each strategy implements the FetchStrategy ABC.
"""

from abc import ABC, abstractmethod


class FetchStrategy(ABC):
    """Base class for all fetch strategies."""

    name: str = "base"

    @abstractmethod
    def fetch(self, url: str, platform: dict) -> dict:
        """
        Fetch content from a URL.

        Args:
            url: The URL to fetch.
            platform: Platform info dict from platforms.identify_platform().

        Returns:
            dict with keys:
                success (bool)
                content (str): Markdown content on success
                metadata (dict): Optional metadata
                strategy (str): Strategy name
                error (str): Error message on failure
        """
        ...
