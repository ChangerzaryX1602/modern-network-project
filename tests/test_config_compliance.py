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
        config = device_outputs[device_name]["info flat /"]
        pattern = inventory[device_name]["expected"]["hostname_pattern"]

        match = re.search(r"host-name\s+(\S+)", config)
        assert match, f"{device_name}: No hostname found in config"

        hostname = match.group(1)
        assert re.match(pattern, hostname), (
            f"{device_name}: Hostname '{hostname}' does not match "
            f"pattern '{pattern}'"
        )


@pytest.mark.parametrize("device_name", DEVICE_NAMES)
class TestNTPConfigured:
    """Verify NTP server is configured."""

    def test_ntp_configured(self, device_name, device_outputs, inventory):
        config = device_outputs[device_name]["info flat /"]
        expected_ntp = inventory[device_name]["expected"]["ntp_server"]

        assert f"ntp server {expected_ntp}" in config, (
            f"{device_name}: NTP server {expected_ntp} not configured"
        )


@pytest.mark.parametrize("device_name", DEVICE_NAMES)
class TestLoggingEnabled:
    """Verify syslog/logging is configured."""

    def test_logging_remote_server(self, device_name, device_outputs):
        config = device_outputs[device_name]["info flat /"]
        assert re.search(r"logging remote-server \S+", config), (
            f"{device_name}: No logging remote-server configured"
        )


@pytest.mark.parametrize("device_name", DEVICE_NAMES)
class TestNetworkInstancesExist:
    """Verify required network-instances (VLAN equivalent) are present."""

    def test_network_instances_exist(
        self, device_name, device_outputs, inventory
    ):
        output = device_outputs[device_name]["show network-instance summary"]
        expected = inventory[device_name]["expected"]["network_instances"]

        for ni_name in expected:
            assert ni_name in output, (
                f"{device_name}: Network-instance {ni_name} not found\n{output}"
            )
