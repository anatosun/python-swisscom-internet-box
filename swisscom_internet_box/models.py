"""Data models for the Swisscom Internet-Box API."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class BoxInfo:
    """Static information about the Internet-Box itself."""

    manufacturer: str
    model_name: str
    product_class: str
    serial_number: str
    hardware_version: str
    software_version: str
    base_mac: str
    up_time: int
    device_status: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BoxInfo:
        return cls(
            manufacturer=data.get("Manufacturer", ""),
            model_name=data.get("ModelName", ""),
            product_class=data.get("ProductClass", ""),
            serial_number=data.get("SerialNumber", ""),
            hardware_version=data.get("HardwareVersion", ""),
            software_version=data.get("SoftwareVersion", ""),
            base_mac=data.get("BaseMAC", ""),
            up_time=data.get("UpTime", 0),
            device_status=data.get("DeviceStatus", ""),
        )


@dataclass
class WANStatus:
    """Current WAN connection state."""

    link_type: str
    link_state: str
    protocol: str
    connection_state: str

    @property
    def is_connected(self) -> bool:
        return self.link_state == "up" and self.connection_state == "Bound"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WANStatus:
        return cls(
            link_type=data.get("LinkType", ""),
            link_state=data.get("LinkState", ""),
            protocol=data.get("Protocol", ""),
            connection_state=data.get("ConnectionState", ""),
        )


@dataclass
class NMCInfo:
    """Top-level NMC configuration."""

    wan_mode: str
    active_wan_interface: str
    provisioning_state: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> NMCInfo:
        return cls(
            wan_mode=data.get("WanMode", ""),
            active_wan_interface=data.get("ActiveWANInterface", ""),
            provisioning_state=data.get("ProvisioningState", ""),
        )


@dataclass
class WiFiStatus:
    """Current WiFi radio state."""

    enabled: bool
    active: bool
    wps_enabled: bool
    scheduler_enabled: bool

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WiFiStatus:
        return cls(
            enabled=data.get("Enable", False),
            active=data.get("Status", False),
            wps_enabled=data.get("WPSEnable", False),
            scheduler_enabled=data.get("Scheduler", False),
        )


@dataclass
class IPv4Address:
    """IPv4 address entry for a device."""

    address: str
    status: str
    scope: str
    address_source: str
    reserved: bool

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> IPv4Address:
        return cls(
            address=data.get("Address", ""),
            status=data.get("Status", ""),
            scope=data.get("Scope", ""),
            address_source=data.get("AddressSource", ""),
            reserved=data.get("Reserved", False),
        )


@dataclass
class IPv6Address:
    """IPv6 address entry for a device."""

    address: str
    status: str
    scope: str
    address_source: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> IPv6Address:
        return cls(
            address=data.get("Address", ""),
            status=data.get("Status", ""),
            scope=data.get("Scope", ""),
            address_source=data.get("AddressSource", ""),
        )


@dataclass
class Bandwidth:
    """Bandwidth counters for a device over a time window."""

    period: str
    rx_bytes: int
    tx_bytes: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Bandwidth:
        return cls(
            period=data.get("Id", ""),
            rx_bytes=data.get("RxBytes", 0),
            tx_bytes=data.get("TxBytes", 0),
        )


@dataclass
class AccessPoint:
    """A WiFi access point (VAP) on the Internet-Box.

    Regular SSIDs have keys like ``wl0`` / ``wl1``.
    The guest network has a key like ``wlguest2``.
    """

    key: str
    ssid: str
    bssid: str
    enabled: bool
    frequency_band: str
    operating_standards: str
    channel: int

    @property
    def is_guest(self) -> bool:
        return "guest" in self.key.lower()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AccessPoint:
        return cls(
            key=data.get("Key", ""),
            ssid=data.get("SSID", ""),
            bssid=data.get("BSSID", ""),
            enabled=data.get("Enabled", False),
            frequency_band=data.get("OperatingFrequencyBand", ""),
            operating_standards=data.get("OperatingStandards", ""),
            channel=data.get("Channel", 0),
        )


@dataclass
class Device:
    """A LAN device known to the Internet-Box."""

    key: str
    name: str
    device_type: str
    active: bool
    phys_address: str
    ip_address: str
    ip_address_source: str
    interface_name: str
    layer2_interface: str
    mac_vendor: str
    first_seen: str
    last_connection: str
    ipv4_addresses: list[IPv4Address] = field(default_factory=list)
    ipv6_addresses: list[IPv6Address] = field(default_factory=list)
    bandwidth: list[Bandwidth] = field(default_factory=list)
    signal_strength: int | None = None
    signal_noise_ratio: int | None = None

    @property
    def is_wireless(self) -> bool:
        return "wl" in self.layer2_interface.lower() or "wifi" in self.interface_name.lower()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Device:
        ssw = data.get("SSWSta") or {}
        return cls(
            key=data.get("Key", ""),
            name=data.get("Name", ""),
            device_type=data.get("DeviceType", ""),
            active=data.get("Active", False),
            phys_address=data.get("PhysAddress", ""),
            ip_address=data.get("IPAddress", ""),
            ip_address_source=data.get("IPAddressSource", ""),
            interface_name=data.get("InterfaceName", ""),
            layer2_interface=data.get("Layer2Interface", ""),
            mac_vendor=data.get("MACVendor", ""),
            first_seen=data.get("FirstSeen", ""),
            last_connection=data.get("LastConnection", ""),
            ipv4_addresses=[IPv4Address.from_dict(a) for a in data.get("IPv4Address", [])],
            ipv6_addresses=[IPv6Address.from_dict(a) for a in data.get("IPv6Address", [])],
            bandwidth=[Bandwidth.from_dict(b) for b in data.get("Bandwidth", [])],
            signal_strength=data.get("SignalStrength"),
            signal_noise_ratio=data.get("SignalNoiseRatio"),
        )
