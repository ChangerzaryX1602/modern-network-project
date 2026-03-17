import os
import yaml
import pytest
from netmiko import ConnectHandler


INVENTORY_PATH = os.path.join(
    os.path.dirname(__file__), "..", "inventory", "hosts.yml"
)


def load_inventory():
    with open(INVENTORY_PATH) as f:
        return yaml.safe_load(f)["devices"]


@pytest.fixture(scope="session")
def inventory():
    """Load device inventory from hosts.yml."""
    return load_inventory()


@pytest.fixture(scope="session")
def device_connections(inventory):
    """Establish SSH connections to all devices via Netmiko.

    Returns a dict: {device_name: ConnectHandler}
    Connections are shared across the entire test session and closed at the end.
    """
    connections = {}
    for name, device in inventory.items():
        conn = ConnectHandler(
            device_type=device["platform"],
            host=device["hostname"],
            username=device["username"],
            password=device["password"],
            timeout=30,
        )
        connections[name] = conn
    yield connections
    for conn in connections.values():
        conn.disconnect()


@pytest.fixture(scope="session")
def device_outputs(device_connections):
    """Pre-collect common show commands from all devices.

    Caches output so multiple tests don't re-run the same commands.
    Returns: {device_name: {command: output}}
    """
    commands = [
        "show ip interface brief",
        "show ip route",
        "show running-config",
        "show vlan brief",
        "show ntp status",
        "show access-lists",
    ]
    outputs = {}
    for name, conn in device_connections.items():
        outputs[name] = {}
        for cmd in commands:
            outputs[name][cmd] = conn.send_command(cmd)
    return outputs


def run_command(device_connections, device_name, command):
    """Helper to run an ad-hoc command on a specific device."""
    return device_connections[device_name].send_command(command)
