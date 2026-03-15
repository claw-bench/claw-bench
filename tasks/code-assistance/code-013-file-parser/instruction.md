# Task: Write a Config File Parser

Write a parser in `workspace/parser.py` for a custom INI-like config format.

## Config Format

```ini
# This is a comment
; This is also a comment

[section_name]
key = value
number = 42
flag = true

[another_section]
path = /usr/local/bin
```

## Requirements

Implement a function `parse_config(filepath: str) -> dict` that:

1. Reads the config file at the given path.
2. Returns a nested dict: `{"section_name": {"key": "value", "number": 42, "flag": True}, ...}`.
3. Lines starting with `#` or `;` are comments and should be ignored.
4. Empty lines should be ignored.
5. Type coercion: values that look like integers should become `int`, `"true"`/`"false"` (case-insensitive) should become `bool`, everything else stays `str`.
6. Raise `ValueError` for malformed lines (non-empty, non-comment lines that are not section headers or key=value pairs).
7. Key-value pairs before any section header should raise `ValueError`.

Also implement `parse_config_string(text: str) -> dict` that works the same way but on a string instead of a file.

## Output

Save the file to `workspace/parser.py`. A sample config file `workspace/sample.conf` is provided for testing.
