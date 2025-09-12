# app/utils/status_converter.py
"""Status enum conversion utilities."""

import logging
from typing import Union
from app.models.submission import SubmissionStatus

logger = logging.getLogger(__name__)


class StatusConverter:
    """Handle status string to enum conversions."""

    STATUS_MAPPING = {
        "pending": SubmissionStatus.PENDING,
        "processing": SubmissionStatus.PROCESSING,
        "success": SubmissionStatus.SUCCESS,
        "failed": SubmissionStatus.FAILED,
        "completed": SubmissionStatus.SUCCESS,
        "retrying": SubmissionStatus.PROCESSING,
    }

    @classmethod
    def to_enum(cls, status: Union[str, SubmissionStatus]) -> SubmissionStatus:
        """
        Convert status string to enum.

        Args:
            status: Status string or enum

        Returns:
            SubmissionStatus enum
        """
        if isinstance(status, SubmissionStatus):
            return status

        # Try lowercase mapping first
        status_lower = status.lower() if status else "pending"
        if status_lower in cls.STATUS_MAPPING:
            return cls.STATUS_MAPPING[status_lower]

        # Try uppercase mapping
        status_upper = status.upper() if status else "PENDING"
        if status_upper in cls.STATUS_MAPPING:
            return cls.STATUS_MAPPING[status_upper]

        # Try direct enum creation
        try:
            return SubmissionStatus(status_upper)
        except ValueError:
            logger.warning(f"Invalid status '{status}', defaulting to PENDING")
            return SubmissionStatus.PENDING
