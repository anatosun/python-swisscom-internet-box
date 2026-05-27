"""Authenticated client for the Swisscom Internet-Box web-services endpoint."""

from __future__ import annotations

from typing import Any

import aiohttp

from .exceptions import SwisscomAuthError, SwisscomConnectionError
from .models import AccessPoint, BoxInfo, Device, NMCInfo, WANStatus, WiFiStatus

CONTENT_TYPE = "application/x-sah-ws-4-call+json"
REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=10)


class SwisscomClient:
    """Authenticated client for the Internet-Box web-services endpoint."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        host: str,
        username: str,
        password: str,
    ) -> None:
        """Initialize the client."""
        self._session = session
        self._url = f"http://{host}/ws"
        self._username = username
        self._password = password
        self._context_id: str | None = None

    async def _post(
        self, payload: dict[str, Any], headers: dict[str, str]
    ) -> dict[str, Any]:
        """POST a request and return the parsed JSON body."""
        try:
            async with self._session.post(
                self._url,
                json=payload,
                headers={"Content-Type": CONTENT_TYPE, **headers},
                timeout=REQUEST_TIMEOUT,
            ) as response:
                if response.status == 401:
                    raise SwisscomAuthError("Unauthorized")
                response.raise_for_status()
                return await response.json(content_type=None)
        except (TimeoutError, aiohttp.ClientError) as err:
            raise SwisscomConnectionError(str(err)) from err

    async def _post_authenticated(self, payload: dict[str, Any]) -> dict[str, Any]:
        """POST a request with the current context ID, re-authenticating once on expiry."""
        if self._context_id is None:
            await self.login()

        for attempt in range(2):
            assert self._context_id is not None
            try:
                return await self._post(
                    payload,
                    {
                        "Authorization": f"X-Sah {self._context_id}",
                        "X-Context": self._context_id,
                    },
                )
            except SwisscomAuthError:
                if attempt == 0:
                    await self.login()
                    continue
                raise
        return {}

    async def login(self) -> None:
        """Authenticate and store a context ID."""
        data = await self._post(
            {
                "service": "sah.Device.Information",
                "method": "createContext",
                "parameters": {
                    "applicationName": "webui",
                    "username": self._username,
                    "password": self._password,
                },
            },
            {"Authorization": "X-Sah-Login"},
        )
        try:
            self._context_id = data["data"]["contextID"]
        except (KeyError, TypeError) as err:
            raise SwisscomAuthError("Unexpected authentication response") from err

    async def get_box_info(self) -> BoxInfo:
        """Return static information about the Internet-Box (unauthenticated)."""
        data = await self._post(
            {"service": "DeviceInfo", "method": "get", "parameters": {}}, {}
        )
        return BoxInfo.from_dict(data.get("status", {}))

    async def get_wan_status(self) -> WANStatus:
        """Return current WAN connection state (unauthenticated)."""
        data = await self._post(
            {"service": "NMC", "method": "getWANStatus", "parameters": {}}, {}
        )
        return WANStatus.from_dict(data.get("data", {}))

    async def get_nmc_info(self) -> NMCInfo:
        """Return top-level NMC configuration (WAN mode, interface, provisioning)."""
        data = await self._post(
            {"service": "NMC", "method": "get", "parameters": {}}, {}
        )
        return NMCInfo.from_dict(data.get("status", {}))

    async def get_wifi_status(self) -> WiFiStatus:
        """Return WiFi radio status."""
        data = await self._post(
            {"service": "NMC.Wifi", "method": "get", "parameters": {}}, {}
        )
        return WiFiStatus.from_dict(data.get("data", {}))

    async def get_access_points(self) -> list[AccessPoint]:
        """Return all WiFi access points (VAPs), including the guest network.

        Use ``ap.is_guest`` to distinguish guest from regular APs.
        """
        data = await self._post_authenticated(
            {
                "service": "Devices",
                "method": "get",
                "parameters": {"expression": "lan and vap"},
            }
        )
        return [AccessPoint.from_dict(d) for d in data.get("status", [])]

    async def get_devices(self, expression: str = "lan and not self") -> list[Device]:
        """Return LAN devices matching the given expression.

        Common expressions:
          ``"lan and not self"``  – all LAN clients (default)
          ``"wifi"``              – wireless clients only
          ``"eth"``               – wired clients only
          ``"lan"``               – all LAN clients including the box itself
        """
        data = await self._post_authenticated(
            {
                "service": "Devices",
                "method": "get",
                "parameters": {"expression": expression},
            }
        )
        return [Device.from_dict(d) for d in data.get("status", [])]
