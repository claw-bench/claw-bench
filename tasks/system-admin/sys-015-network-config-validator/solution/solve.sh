#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

python - "$WORKSPACE" << 'PYEOF'
import sys
import json

ws = sys.argv[1]


def is_valid_ipv4(ip):
    """Check if string is a valid IPv4 address."""
    parts = ip.split(".")
    if len(parts) != 4:
        return False
    for part in parts:
        try:
            val = int(part)
            if val < 0 or val > 255:
                return False
            if part != str(val):
                return False
        except ValueError:
            return False
    return True


def ip_to_int(ip):
    """Convert IPv4 string to 32-bit integer."""
    parts = ip.split(".")
    return (int(parts[0]) << 24) | (int(parts[1]) << 16) | (int(parts[2]) << 8) | int(parts[3])


def is_valid_subnet(mask):
    """Check if subnet mask has contiguous 1-bits then contiguous 0-bits."""
    if not is_valid_ipv4(mask):
        return False
    val = ip_to_int(mask)
    if val == 0:
        return True
    # Check contiguous: invert, add 1, should be power of 2
    inverted = val ^ 0xFFFFFFFF
    return (inverted & (inverted + 1)) == 0


def get_network(ip_int, mask_int):
    return ip_int & mask_int


def get_broadcast(ip_int, mask_int):
    host_bits = mask_int ^ 0xFFFFFFFF
    return (ip_int & mask_int) | host_bits


with open(f"{ws}/network_config.json") as f:
    interfaces = json.load(f)

results = []
valid_count = 0
invalid_count = 0

for iface in interfaces:
    errors = []
    name = iface["name"]
    ip = iface["ip"]
    subnet = iface["subnet_mask"]
    gateway = iface["gateway"]
    dns_list = iface["dns"]

    ip_valid = is_valid_ipv4(ip)
    subnet_valid = is_valid_subnet(subnet)
    gw_valid = is_valid_ipv4(gateway)

    if not ip_valid:
        errors.append(f"invalid_ip: {ip} is not a valid IPv4 address")

    if not subnet_valid:
        errors.append(f"invalid_subnet: {subnet} is not a valid subnet mask")

    if not gw_valid:
        errors.append(f"invalid_gateway: {gateway} is not a valid IPv4 address")

    for dns in dns_list:
        if not is_valid_ipv4(dns):
            errors.append(f"invalid_dns: {dns} is not a valid IPv4 address")

    # Only check subnet-related rules if IP, subnet, and gateway are all valid
    if ip_valid and subnet_valid and gw_valid:
        ip_int = ip_to_int(ip)
        mask_int = ip_to_int(subnet)
        gw_int = ip_to_int(gateway)

        net_ip = get_network(ip_int, mask_int)
        net_gw = get_network(gw_int, mask_int)

        if net_ip != net_gw:
            errors.append(
                f"gateway_not_in_subnet: gateway {gateway} is not in the same subnet as {ip}/{subnet}"
            )

        if ip_int == net_ip:
            errors.append(
                f"ip_is_network_address: {ip} is the network address"
            )

        bcast = get_broadcast(ip_int, mask_int)
        if ip_int == bcast:
            errors.append(
                f"ip_is_broadcast_address: {ip} is the broadcast address"
            )

    is_valid = len(errors) == 0
    if is_valid:
        valid_count += 1
    else:
        invalid_count += 1

    results.append({
        "name": name,
        "ip": ip,
        "subnet_mask": subnet,
        "gateway": gateway,
        "dns": dns_list,
        "valid": is_valid,
        "errors": errors
    })

report = {
    "interfaces": results,
    "summary": {
        "total_interfaces": len(results),
        "valid_count": valid_count,
        "invalid_count": invalid_count
    }
}

with open(f"{ws}/validation_report.json", "w") as f:
    json.dump(report, f, indent=2)
PYEOF
