# Task: Network Config Validator

You are given a file at `workspace/network_config.json` containing an array of network interface configurations.

## Requirements

1. Read `workspace/network_config.json`.
2. Each interface has: `name`, `ip`, `subnet_mask`, `gateway`, and `dns` (array of DNS server IPs).
3. Validate each interface for the following errors:

### Validation Rules

- **invalid_ip**: The `ip` field must be a valid IPv4 address (four octets, each 0-255).
- **invalid_subnet**: The `subnet_mask` must be a valid subnet mask (contiguous 1-bits followed by contiguous 0-bits when expressed in binary, e.g., 255.255.255.0 is valid, 255.255.0.255 is not).
- **invalid_gateway**: The `gateway` must be a valid IPv4 address.
- **invalid_dns**: Each DNS server must be a valid IPv4 address. Report if any are invalid.
- **gateway_not_in_subnet**: The gateway must be in the same subnet as the interface IP. Apply the subnet mask to both the IP and gateway; they must produce the same network address.
- **ip_is_network_address**: The IP should not be the network address itself (all host bits zero).
- **ip_is_broadcast_address**: The IP should not be the broadcast address (all host bits one).

4. Generate `workspace/validation_report.json` with this structure:

```json
{
  "interfaces": [
    {
      "name": "<name>",
      "ip": "<ip>",
      "subnet_mask": "<mask>",
      "gateway": "<gateway>",
      "dns": ["<dns1>", ...],
      "valid": true,
      "errors": []
    },
    ...
  ],
  "summary": {
    "total_interfaces": 6,
    "valid_count": 3,
    "invalid_count": 3
  }
}
```

5. Each error in the `errors` array should be a string describing the issue (use the error codes above as prefixes, e.g., "invalid_ip: 999.1.1.1 is not a valid IPv4 address").
6. An interface is `valid` only if it has zero errors.

## Output

Save the report to `workspace/validation_report.json`.
