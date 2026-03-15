# Task: Create a Data Validation Module

Create a data validation module in `workspace/validator.py` with validators for common data formats.

## Requirements

Implement the following five validator functions. Each must return a tuple `(bool, str)` where the bool indicates whether the input is valid and the string is an error message (empty string if valid).

1. **`validate_email(email: str) -> tuple[bool, str]`**
   - Must contain exactly one `@` with non-empty local and domain parts.
   - Domain must contain at least one dot.
   - Example valid: `user@example.com`
   - Example invalid: `user@`, `@domain.com`, `user@domain`

2. **`validate_phone(phone: str) -> tuple[bool, str]`**
   - Accept formats: `1234567890`, `123-456-7890`, `(123) 456-7890`, `+1-123-456-7890`
   - Must have 10 digits (excluding country code).
   - Example invalid: `123`, `abc-def-ghij`

3. **`validate_url(url: str) -> tuple[bool, str]`**
   - Must start with `http://` or `https://`.
   - Must have a valid domain after the scheme.
   - Example valid: `https://example.com`, `http://example.com/path`
   - Example invalid: `ftp://example.com`, `example.com`, `https://`

4. **`validate_date(date_str: str) -> tuple[bool, str]`**
   - Accept format `YYYY-MM-DD`.
   - Must be a valid calendar date.
   - Example valid: `2024-01-15`
   - Example invalid: `2024-13-01`, `2024-02-30`, `not-a-date`

5. **`validate_ip(ip: str) -> tuple[bool, str]`**
   - Validate IPv4 addresses (four octets, each 0-255).
   - Example valid: `192.168.1.1`, `0.0.0.0`
   - Example invalid: `256.1.1.1`, `1.2.3`, `1.2.3.4.5`

## Output

Save the file to `workspace/validator.py`.
