# Task: Multi-File Refactoring

You are given a small application in `workspace/app/` with three files: `models.py`, `views.py`, and `utils.py`. These files contain duplicated logic that should be extracted into a shared base module.

## Current Structure

- `workspace/app/models.py` -- Data model classes with duplicated validation and serialization logic.
- `workspace/app/views.py` -- View handlers with duplicated response formatting and error handling.
- `workspace/app/utils.py` -- Utility functions with duplicated string processing helpers.

## Requirements

1. Create a new file `workspace/app/base.py` that contains the shared/extracted logic.
2. Refactor the three existing files to import from `base.py` instead of duplicating code.
3. All original classes and functions must still exist and work correctly.
4. The `workspace/app/__init__.py` must expose the same public API.
5. No code duplication: identical or near-identical logic must appear only in `base.py`.

## Output

Save all files in `workspace/app/`.
