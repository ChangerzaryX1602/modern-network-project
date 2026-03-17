"""Security policy tests — verify devices meet security requirements."""

import re
import pytest
from conftest import load_inventory


INVENTORY = load_inventory()
DEVICE_NAMES = list(INVENTORY.keys())


@pytest.mark.parametrize("device_name", DEVICE_NAMES)
class TestSSHOnly:
    """Verify SSH is enabled and Telnet is disabled."""

    def test_ssh_enabled(self, device_name, device_outputs):
        config = device_outputs[device_name]["show running-config"]
        assert "transport input ssh" in config, (
            f"{device_name}: SSH-only transport not configured on VTY lines"
        )

    def test_telnet_disabled(self, device_name, device_outputs):
        config = device_outputs[device_name]["show running-config"]
        # Ensure telnet is not explicitly allowed
        assert "transport input telnet" not in config, (
            f"{device_name}: Telnet is still enabled on VTY lines"
        )
        assert "transport input all" not in config, (
            f"{device_name}: 'transport input all' allows Telnet on VTY lines"
        )


@pytest.mark.parametrize("device_name", DEVICE_NAMES)
class TestACLApplied:
    """Verify management ACL is applied."""

    def test_acl_exists(self, device_name, device_outputs):
        acl_output = device_outputs[device_name]["show access-lists"]
        assert "MGMT-ACL" in acl_output, (
            f"{device_name}: MGMT-ACL not found in access lists"
        )

    def test_acl_permits_ssh(self, device_name, device_outputs):
        acl_output = device_outputs[device_name]["show access-lists"]
        assert re.search(r"permit tcp any any eq 22", acl_output), (
            f"{device_name}: MGMT-ACL does not permit SSH (port 22)"
        )

    def test_acl_denies_telnet(self, device_name, device_outputs):
        acl_output = device_outputs[device_name]["show access-lists"]
        assert re.search(r"deny tcp any any eq 23", acl_output), (
            f"{device_name}: MGMT-ACL does not deny Telnet (port 23)"
        )

    def test_acl_applied_to_vty(self, device_name, device_outputs):
        config = device_outputs[device_name]["show running-config"]
        assert "access-class MGMT-ACL in" in config, (
            f"{device_name}: MGMT-ACL not applied to VTY lines"
        )


@pytest.mark.parametrize("device_name", DEVICE_NAMES)
class TestPasswordEncryption:
    """Verify password encryption is enabled."""

    def test_password_encryption(self, device_name, device_outputs):
        config = device_outputs[device_name]["show running-config"]
        assert "service password-encryption" in config, (
            f"{device_name}: 'service password-encryption' not enabled"
        )


@pytest.mark.parametrize("device_name", DEVICE_NAMES)
class TestBannerConfigured:
    """Verify login banner is configured."""

    def test_banner_configured(self, device_name, device_outputs):
        config = device_outputs[device_name]["show running-config"]
        assert re.search(r"banner login", config), (
            f"{device_name}: Login banner not configured"
        )
