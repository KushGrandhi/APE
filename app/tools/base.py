"""Base interface for all dock tool integrations."""

from abc import ABC, abstractmethod


class InventorySource(ABC):
    """Interface for looking up expected inventory by time slot."""

    @abstractmethod
    def get_expectation(self, time: str) -> str:
        """Return expected inventory description for a given time slot."""
        ...


class VisionSource(ABC):
    """Interface for analyzing dock camera feeds."""

    @abstractmethod
    def observe(self, source: str) -> str:
        """Observe the dock and return a description of containers and hazard symbols.

        Args:
            source: An image path, directory of images, camera index ("0"),
                    or RTSP URL depending on the implementation.
        """
        ...


class AudioSource(ABC):
    """Interface for processing dock worker voice input."""

    @abstractmethod
    def listen(self, source: str) -> str:
        """Listen and return transcribed voice instruction.

        Args:
            source: An audio file path or empty string for microphone,
                    depending on the implementation.
        """
        ...


class GestureSource(ABC):
    """Interface for recognizing dock worker gestures."""

    @abstractmethod
    def read_gesture(self, source: str) -> str:
        """Observe a dock worker and return interpreted gesture.

        Args:
            source: An image path, directory of images, camera index ("0"),
                    or RTSP URL depending on the implementation.

        Returns:
            Description of the detected gesture and its interpretation
            as one of: 'approve', 'review', or 'decline'.
        """
        ...
