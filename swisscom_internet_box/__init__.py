"""Python client for the Swisscom Internet-Box."""

from .client import SwisscomClient
from .exceptions import SwisscomAuthError, SwisscomConnectionError, SwisscomError
from .models import (
    AccessPoint,
    Bandwidth,
    BoxInfo,
    Device,
    IPv4Address,
    IPv6Address,
    NMCInfo,
    WANStatus,
    WiFiStatus,
)

__all__ = [
    "SwisscomClient",
    "SwisscomError",
    "SwisscomAuthError",
    "SwisscomConnectionError",
    "AccessPoint",
    "BoxInfo",
    "WANStatus",
    "NMCInfo",
    "WiFiStatus",
    "Device",
    "IPv4Address",
    "IPv6Address",
    "Bandwidth",
]
