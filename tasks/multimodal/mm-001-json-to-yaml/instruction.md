# JSON to YAML Conversion

You have a file `config.json` in your workspace that contains a complex nested JSON configuration for a web application.

**Task:** Convert `config.json` to YAML format and save the output as `config.yaml` in the workspace.

## Requirements

- Preserve all nested structure exactly (objects, arrays, nested objects within arrays)
- Preserve all data types: strings, numbers, booleans, null values
- The output must be valid YAML that can be parsed back to the same data structure
- Use standard YAML formatting (2-space indentation, no trailing whitespace)
- Do not add YAML document markers (`---`) at the top
- Array items should use `- ` prefix notation
