"""Reachability tests — verify connectivity between network devices."""

import pytest
from conftest import load_inventory, run_command


INVENTORY = load_inventory()
DEVICE_NAMES = list(INVENTORY.keys())


@pytest.mark.parametrize("device_name", DEVICE_NAMES)
class TestInterfacesUp:
    """Verify that expected interfaces are in up/up state."""

    def test_interfaces_up(self, device_name, device_outputs, inventory):
        expected_interfaces = inventory[device_name]["expected"]["interfaces_up"]
        output = device_outputs[device_name]["show ip interface brief"]

        for iface in expected_interfaces:
            # Find the line for this interface
            matching_lines = [
                line for line in output.splitlines() if iface in line
            ]
            assert matching_lines, (
                f"{device_name}: Interface {iface} not found in output"
            )
            line = matching_lines[0]
            assert "up" in line.lower(), (
                f"{device_name}: Interface {iface} is not up — {line.strip()}"
            )


@pytest.mark.parametrize("device_name", DEVICE_NAMES)
class TestPingReachability:
    """Verify ping connectivity to expected targets."""

    def test_ping_between_devices(
        self, device_name, device_connections, inventory
    ):
        targets = inventory[device_name]["expected"]["ping_targets"]
        for target in targets:
            output = run_command(
                device_connections, device_name, f"ping {target} repeat 3"
            )
            # Cisco ping output: Success rate is X percent
            assert "success rate is 100" in output.lower() or "!!" in output, (
                f"{device_name}: Ping to {target} failed\n{output}"
            )


@pytest.mark.parametrize("device_name", DEVICE_NAMES)
class TestRoutingTable:
    """Verify expected routes exist in the routing table."""

    def test_routing_table_entries(
        self, device_name, device_outputs, inventory
    ):
        output = device_outputs[device_name]["show ip route"]
        targets = inventory[device_name]["expected"]["ping_targets"]

        for target in targets:
            # Extract network portion (first 3 octets for /24 assumption)
            network = ".".join(target.split(".")[:3])
            assert network in output, (
                f"{device_name}: No route found for network {network}\n{output}"
            )
