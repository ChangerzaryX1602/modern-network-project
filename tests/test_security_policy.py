"""Security policy tests — verify devices meet security requirements."""

import re
import pytest
from conftest import load_inventory


INVENTORY = load_inventory()
DEVICE_NAMES = list(INVENTORY.keys())


@pytest.mark.parametrize("device_name", DEVICE_NAMES)
class TestSSHEnabled:
    """Verify SSH server is running."""

    def test_ssh_enabled(self, device_name, device_outputs):
        config = device_outputs[device_name]["info flat /"]
        assert "ssh-server" in config, (
            f"{device_name}: SSH server not configured"
        )


@pytest.mark.parametrize("device_name", DEVICE_NAMES)
class TestACLApplied:
    """Verify management ACL filter is applied."""

    def test_acl_exists(self, device_name, device_outputs):
        config = device_outputs[device_name]["info flat /"]
        assert "MGMT-FILTER" in config, (
            f"{device_name}: MGMT-FILTER not found in config"
        )

    def test_acl_permits_ssh(self, device_name, device_outputs):
        config = device_outputs[device_name]["info flat /"]
        assert re.search(r"destination-port value 22", config), (
            f"{device_name}: MGMT-FILTER does not permit SSH (port 22)"
        )
        assert re.search(
            r"MGMT-FILTER type ipv4 entry 100 action accept", config
        ), (
            f"{device_name}: SSH entry does not have accept action"
        )

    def test_acl_denies_telnet(self, device_name, device_outputs):
        config = device_outputs[device_name]["info flat /"]
        assert re.search(r"destination-port value 23", config), (
            f"{device_name}: MGMT-FILTER does not reference Telnet (port 23)"
        )
        assert re.search(
            r"MGMT-FILTER type ipv4 entry 110 action drop", config
        ), (
            f"{device_name}: Telnet entry does not have drop action"
        )


@pytest.mark.parametrize("device_name", DEVICE_NAMES)
class TestBannerConfigured:
    """Verify login banner is configured."""

    def test_banner_configured(self, device_name, device_outputs):
        config = device_outputs[device_name]["info flat /"]
        assert re.search(r"login-banner", config), (
            f"{device_name}: Login banner not configured"
        )
