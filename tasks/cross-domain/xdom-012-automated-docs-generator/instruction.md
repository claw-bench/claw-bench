# Task: Automated Documentation Generator

Analyze Python source modules and generate comprehensive documentation.

## Input Files

Five Python modules in `workspace/source_code/`:
- `models.py` - Data models
- `database.py` - Database operations
- `api.py` - API endpoints
- `auth.py` - Authentication
- `utils.py` - Utility functions

## Objective

Generate four documentation files:

1. `workspace/api_docs.md` - API reference documentation
2. `workspace/architecture.md` - Architecture overview
3. `workspace/getting_started.md` - Getting started guide
4. `workspace/index.json` - Documentation index

## Output: api_docs.md

- Document every public function and class from all 5 modules
- Include function signatures with type hints
- Include docstring content
- Include parameter descriptions
- Include return type information
- Organize by module

## Output: architecture.md

- High-level system description
- Module dependency diagram (text-based)
- Description of each module's responsibility
- Data flow description

## Output: getting_started.md

- Installation steps
- Configuration requirements
- Basic usage examples (at least 3)
- Common operations walkthrough

## Output: index.json

```json
{
  "title": "Project Documentation",
  "documents": [
    {
      "file": "api_docs.md",
      "title": "API Reference",
      "sections": ["module_name", ...]
    }
  ],
  "modules": ["models", "database", "api", "auth", "utils"],
  "total_functions": N,
  "total_classes": N
}
```
