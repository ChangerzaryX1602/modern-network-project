"""Config compliance tests — verify device configurations meet standards."""

import re
import pytest
from conftest import load_inventory


INVENTORY = load_inventory()
DEVICE_NAMES = list(INVENTORY.keys())


@pytest.mark.parametrize("device_name", DEVICE_NAMES)
class TestHostnameStandard:
    """Verify hostname follows the naming convention."""

    def test_hostname_standard(self, device_name, device_outputs, inventory):
        config = device_outputs[device_name]["show running-config"]
        pattern = inventory[device_name]["expected"]["hostname_pattern"]

        # Extract hostname from running config
        match = re.search(r"^hostname\s+(\S+)", config, re.MULTILINE)
        assert match, f"{device_name}: No hostname found in running config"

        hostname = match.group(1)
        assert re.match(pattern, hostname), (
            f"{device_name}: Hostname '{hostname}' does not match "
            f"pattern '{pattern}'"
        )


@pytest.mark.parametrize("device_name", DEVICE_NAMES)
class TestNTPConfigured:
    """Verify NTP server is configured."""

    def test_ntp_configured(self, device_name, device_outputs, inventory):
        config = device_outputs[device_name]["show running-config"]
        expected_ntp = inventory[device_name]["expected"]["ntp_server"]

        assert f"ntp server {expected_ntp}" in config, (
            f"{device_name}: NTP server {expected_ntp} not configured"
        )


@pytest.mark.parametrize("device_name", DEVICE_NAMES)
class TestLoggingEnabled:
    """Verify syslog/logging is configured."""

    def test_logging_buffered(self, device_name, device_outputs):
        config = device_outputs[device_name]["show running-config"]
        assert "logging buffered" in config, (
            f"{device_name}: Buffered logging not configured"
        )

    def test_logging_host(self, device_name, device_outputs):
        config = device_outputs[device_name]["show running-config"]
        assert re.search(r"logging host \S+", config), (
            f"{device_name}: No logging host configured"
        )


@pytest.mark.parametrize("device_name", DEVICE_NAMES)
class TestVLANsExist:
    """Verify required VLANs are present."""

    def test_vlans_exist(self, device_name, device_outputs, inventory):
        output = device_outputs[device_name]["show vlan brief"]
        expected_vlans = inventory[device_name]["expected"]["vlans"]

        for vlan_id in expected_vlans:
            assert str(vlan_id) in output, (
                f"{device_name}: VLAN {vlan_id} not found\n{output}"
            )
