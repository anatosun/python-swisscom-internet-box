# python-swisscom-internet-box

Async Python client for the Swisscom Internet-Box local API (`/ws` endpoint).

## Installation

```bash
pip install python-swisscom-internet-box
```

## Usage

```python
import asyncio
import aiohttp
from swisscom_internet_box import SwisscomClient

async def main():
    async with aiohttp.ClientSession() as session:
        client = SwisscomClient(session, "192.168.1.1", "admin", "your-password")

        # Device info & WAN status (unauthenticated)
        info = await client.get_box_info()
        print(f"{info.model_name} — FW {info.software_version}")

        wan = await client.get_wan_status()
        print(f"WAN: {wan.connection_state} ({wan.protocol})")

        # WiFi access points (includes guest network)
        for ap in await client.get_access_points():
            label = "guest" if ap.is_guest else "main"
            print(f"[{label}] {ap.ssid} — {ap.frequency_band} — {'on' if ap.enabled else 'off'}")

        # Connected LAN devices
        for device in await client.get_devices():
            if device.active:
                print(f"{device.name} — {device.ip_address} — {'wifi' if device.is_wireless else 'eth'}")

asyncio.run(main())
```

## API

### `SwisscomClient(session, host, username, password)`

| Method                    | Auth required | Description                                           |
| ------------------------- | ------------- | ----------------------------------------------------- |
| `get_box_info()`          | No            | Manufacturer, model, firmware, MAC, uptime            |
| `get_wan_status()`        | No            | Link type/state, protocol, connection state           |
| `get_nmc_info()`          | No            | WAN mode, active interface, provisioning state        |
| `get_wifi_status()`       | No            | WiFi global enable/active state                       |
| `get_access_points()`     | Yes           | All VAPs (main + guest); use `ap.is_guest` to filter  |
| `get_devices(expression)` | Yes           | LAN devices; default expression: `"lan and not self"` |

### Device expressions

| Expression           | Result                    |
| -------------------- | ------------------------- |
| `"lan and not self"` | All LAN clients (default) |
| `"wifi"`             | Wireless clients only     |
| `"eth"`              | Wired clients only        |

### Models

- `BoxInfo` — `manufacturer`, `model_name`, `software_version`, `base_mac`, `up_time`, `device_status`
- `WANStatus` — `link_type`, `link_state`, `protocol`, `connection_state`, `.is_connected`
- `NMCInfo` — `wan_mode`, `active_wan_interface`, `provisioning_state`
- `WiFiStatus` — `enabled`, `active`, `wps_enabled`, `scheduler_enabled`
- `AccessPoint` — `key`, `ssid`, `bssid`, `enabled`, `frequency_band`, `channel`, `.is_guest`
- `Device` — `key`, `name`, `phys_address`, `ip_address`, `active`, `interface_name`, `.is_wireless`, `ipv4_addresses`, `ipv6_addresses`, `bandwidth`

## Compatibility

Tested on Internet-Box 4 (IB4-00, firmware 14.20.40). Should work on IB2, IB3 and IB5 running similar firmware.

## License

MIT
