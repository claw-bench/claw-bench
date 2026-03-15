# Architecture Document Generation

You have a Python project directory `project/` in your workspace containing multiple Python modules that form a small web application backend.

**Task:** Analyze the project source code and generate an `architecture.md` file in the workspace documenting the project architecture.

## Requirements

The `architecture.md` must contain the following sections:

### 1. Overview
A level-1 heading `# Architecture Overview` followed by a brief description of the project.

### 2. Modules
A level-2 heading `## Modules` followed by a subsection for each Python file (module) in the project. For each module, include:
- A level-3 heading with the module filename (e.g., `### models.py`)
- A brief description of the module's purpose (based on its docstring or contents)
- A list of public classes and functions defined in the module (those not starting with `_`)

### 3. Dependencies
A level-2 heading `## Dependencies` showing which project modules import from other project modules. Format as a list:
```
- module_a.py -> module_b.py
```
Only include internal project dependencies (not standard library or third-party imports).

### 4. Data Flow
A level-2 heading `## Data Flow` describing how data moves through the system, from incoming requests through the layers to the response. This should mention the key modules in order.

### 5. External Dependencies
A level-2 heading `## External Dependencies` listing third-party packages imported across all modules (not standard library).
