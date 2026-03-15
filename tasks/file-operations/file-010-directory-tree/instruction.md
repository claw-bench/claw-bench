# Task: Directory Tree Listing

You are given a directory structure at `workspace/project/`. Generate a text-based directory tree listing.

## Requirements

1. Traverse the `workspace/project/` directory recursively.
2. Generate a tree listing showing all directories and files.
3. Use indentation of 4 spaces per nesting level.
4. Prefix directories with `[DIR]` and files with `[FILE]`.
5. Sort entries alphabetically at each level, with directories listed before files.
6. Write the result to `workspace/tree.txt`.

## Example

For a structure like:

```
project/
  src/
    main.py
  README.md
```

The output should be:

```
project/
    [DIR] src/
        [FILE] main.py
    [FILE] README.md
```

## Output

Save the tree listing to `workspace/tree.txt`.
