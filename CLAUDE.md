# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Automated Network Testing CI/CD pipeline for Nokia SR Linux devices using Containerlab, PyTest, and GitHub Actions.

## Architecture

- **CI/CD**: GitHub Actions pipeline triggered on every push (all branches)
- **Lab Environment**: Containerlab with Nokia SR Linux images (free, no license required)
- **Device Connectivity**: Netmiko (nokia_srl) for SSH connections to network devices
- **Testing**: PyTest with three test categories:
  - `test_reachability.py` — ping, interface status, routing table validation
  - `test_config_compliance.py` — hostname standards, NTP, logging, network-instances
  - `test_security_policy.py` — ACL filters, SSH access, banners

## Key Directories

- `.github/workflows/` — GitHub Actions pipeline definitions
- `containerlab/` — Containerlab topology files and device configs
- `containerlab/configs/` — SR Linux CLI startup configs (srl1.cli, srl2.cli, srl3.cli)
- `tests/` — PyTest test cases and fixtures (`conftest.py` holds device connection fixtures)
- `inventory/` — Device inventory (hosts.yml)

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Pull SR Linux image
docker pull ghcr.io/nokia/srlinux:latest

# Start Containerlab topology
sudo containerlab deploy -t containerlab/topology.yml

# Run all tests
pytest tests/ -v

# Run single test category
pytest tests/test_reachability.py -v
pytest tests/test_config_compliance.py -v
pytest tests/test_security_policy.py -v

# Destroy lab
sudo containerlab destroy -t containerlab/topology.yml
```

## Conventions

- All device connections go through fixtures in `tests/conftest.py` — do not create ad-hoc connections in test files
- Inventory is the single source of truth for device IPs, credentials, and platform info
- Tests must be idempotent — they verify state, never modify device configuration
- Pipeline must fail-fast: any test failure blocks the workflow
- SR Linux default credentials: admin / NokiaSrl1!
- SR Linux config uses `info flat /` instead of `show running-config`
