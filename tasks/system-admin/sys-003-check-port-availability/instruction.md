# Task: Check Port Availability

You are given a file at `workspace/ports.txt` containing simulated `netstat -tlnp` output showing listening TCP ports on a system.

## Requirements

1. Read `workspace/ports.txt`.
2. Parse each line to extract the port number, protocol, bind address, and associated process.
3. Generate a JSON report with the following structure:

```json
{
  "total_listening_ports": <count>,
  "ports": [
    {
      "port": <port number as integer>,
      "bind_address": "<address>",
      "protocol": "tcp",
      "pid": <pid as integer or null>,
      "process_name": "<name>",
      "service": "<well-known service name or 'unknown'>"
    },
    ...
  ],
  "well_known_ports": [<list of ports <= 1023>],
  "high_ports": [<list of ports > 1023>]
}
```

4. The `ports` array must be sorted by port number ascending.
5. Map well-known ports to their standard service names:
   - 22: ssh, 25: smtp, 53: dns, 80: http, 443: https, 3306: mysql, 5432: postgresql, 6379: redis, 8080: http-alt, 8443: https-alt, 9090: prometheus

## Output

Save the report to `workspace/port_report.json`.
