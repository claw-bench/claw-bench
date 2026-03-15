# Task: Full Project Setup from Brief

Generate a complete Python project from a project brief document.

## Input

- `workspace/project_brief.md` - Description of the desired project

## Objective

Create a complete project structure in `workspace/project/` with all necessary files for a Python CLI tool.

## Required Output Structure

```
workspace/project/
  README.md
  setup.py
  .gitignore
  ci.yml
  src/
    csv_tool/
      __init__.py
      cli.py
      reader.py
      transformer.py
  tests/
    __init__.py
    test_reader.py
    test_transformer.py
```

## Requirements

### README.md
- Project title and description
- Installation instructions
- Usage examples
- A "Features" section
- A "Contributing" section

### setup.py
- Valid Python setup script with `setuptools.setup()`
- Package name, version, description, author
- `entry_points` with `console_scripts`
- `install_requires` list

### .gitignore
- Standard Python gitignore entries (*.pyc, __pycache__, .venv, etc.)

### ci.yml
- A CI configuration (GitHub Actions format) with lint and test steps

### Source Files (src/csv_tool/)
- `__init__.py` with version string
- `cli.py` with argument parsing (argparse)
- `reader.py` with CSV reading functions
- `transformer.py` with data transformation functions

### Test Files (tests/)
- `test_reader.py` with at least 3 test functions
- `test_transformer.py` with at least 3 test functions
- All tests must be syntactically valid Python
- All test functions must have assertions
