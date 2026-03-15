# Task: Conditional File Processing

You are given a configuration file and an input text file. Based on the configuration, apply the correct transformation to the input.

## Input Files

- `workspace/config.json` — contains a `"mode"` field with one of three values:
  - `"uppercase"` — convert all text to uppercase
  - `"lowercase"` — convert all text to lowercase
  - `"reverse"` — reverse the order of lines (last line becomes first)
- `workspace/input.txt` — the text file to transform

## Requirements

1. Read `workspace/config.json` and determine the mode.
2. Read `workspace/input.txt`.
3. Apply the transformation indicated by the mode:
   - `"uppercase"`: convert every character to uppercase
   - `"lowercase"`: convert every character to lowercase
   - `"reverse"`: reverse the order of lines in the file
4. Write the result to `workspace/output.txt`.

## Output

Save the transformed text to `workspace/output.txt`.
