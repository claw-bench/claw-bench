# Code Documentation Extraction

You have a Python source file `data_processor.py` in your workspace.

**Task:** Parse the Python file and extract all docstrings into a structured documentation file called `documentation.md` in the workspace.

## Requirements

The output `documentation.md` must follow this structure:

1. Start with a level-1 heading: `# data_processor`
2. Include the module-level docstring as a paragraph right after the heading
3. For each class, create a level-2 heading: `## ClassName`
   - Include the class docstring as a paragraph
   - For each method in the class, create a level-3 heading: `### ClassName.method_name`
   - Include the method docstring as a paragraph
4. For each standalone function (not inside a class), create a level-2 heading: `## function_name`
   - Include the function docstring as a paragraph
5. Preserve the order in which classes and functions appear in the source file
6. Methods should appear in the order they are defined in the class
7. If a function or method has no docstring, skip it entirely (do not include a heading for it)
8. Strip leading/trailing whitespace from extracted docstrings but preserve internal line structure
