# Task: XML to JSON Conversion

You are given an XML configuration file at `workspace/config.xml`. Convert it into a clean JSON file.

## Requirements

1. Read `workspace/config.xml`.
2. Produce a JSON file with the following mapping rules:
   - Each XML element becomes a JSON object key.
   - XML attributes are stored under an `"@attributes"` key within the element's object.
   - CDATA sections are treated as plain string values.
   - Repeated sibling elements with the same tag name become a JSON array.
   - Text-only elements become string values directly (no wrapping object needed unless they also have attributes).
   - Nested elements become nested objects.
   - Numeric string values should remain as strings (do not auto-convert).
3. The top-level JSON key should be the root XML element name (`"application"`).
4. Write the result to `workspace/config.json` with 2-space indentation.

## Output

Save the JSON output to `workspace/config.json`.
