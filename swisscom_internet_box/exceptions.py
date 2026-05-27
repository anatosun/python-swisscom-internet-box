"""Exceptions for the Swisscom Internet-Box client."""


class SwisscomError(Exception):
    """Base error for the Swisscom Internet-Box client."""


class SwisscomAuthError(SwisscomError):
    """Authentication with the Internet-Box failed."""


class SwisscomConnectionError(SwisscomError):
    """Communication with the Internet-Box failed."""
