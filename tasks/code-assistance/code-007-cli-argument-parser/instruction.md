# Task: Write a CLI Argument Parser

Create a command-line argument parser in `workspace/cli.py` using Python's `argparse` module.

## Requirements

The script must define a function `create_parser()` that returns an `argparse.ArgumentParser` with these arguments:

1. `--input` (required) -- Path to the input file. Help text: "Path to the input file".
2. `--output` (required) -- Path to the output file. Help text: "Path to the output file".
3. `--format` (optional) -- Output format, choices are `csv` or `json`. Default: `json`. Help text: "Output format (csv or json)".
4. `--verbose` (optional) -- A boolean flag (store_true). Default: `False`. Help text: "Enable verbose output".

The script should also have a `main()` function that parses arguments and prints them (for manual testing), but the verifier will only test `create_parser()`.

## Output

Save the file to `workspace/cli.py`.
