# JSON, YAML, and TOML Processing Skill

## Overview
This skill covers reading, writing, validating, and transforming structured
configuration files in JSON, YAML, and TOML formats.

## Reading Config Files

```python
import json, yaml, tomllib  # tomllib is Python 3.11+; use `tomli` for earlier

with open("config.json", "r") as f:
    json_data = json.load(f)
with open("config.yaml", "r") as f:
    yaml_data = yaml.safe_load(f)
with open("config.toml", "rb") as f:
    toml_data = tomllib.load(f)
```

## Key Techniques

- **Schema validation**: Use `jsonschema` to validate JSON or YAML against a schema.
- **Deep merging**: Merge nested dicts with libraries like `deepmerge` or a recursive helper.
- **Environment overrides**: Layer config sources (defaults < file < env vars) for flexibility.
- **Anchors and aliases**: YAML supports `&anchor` / `*alias` to reduce duplication.

## Cross-Format Conversion

```python
import json, yaml

# YAML to JSON
with open("input.yaml") as f:
    data = yaml.safe_load(f)
with open("output.json", "w") as f:
    json.dump(data, f, indent=2, default=str)
```

When converting between formats, watch for type differences: YAML auto-casts
`yes`/`no` to booleans and bare numbers to ints or floats.

## Writing Config Files

```python
with open("output.yaml", "w") as f:
    yaml.dump(data, f, default_flow_style=False, sort_keys=False)
```

## Tips
- Always use `yaml.safe_load` instead of `yaml.load` to prevent arbitrary code execution.
- Prefer `tomllib` over regex parsing for TOML; the format has subtle quoting rules.
- Validate config files early in your pipeline to surface errors before downstream steps.
- Preserve key ordering with `sort_keys=False` when round-tripping YAML or JSON.
- Handle missing keys with `dict.get(key, default)` rather than bare indexing.
