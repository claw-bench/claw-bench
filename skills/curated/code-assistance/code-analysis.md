# Code Analysis Patterns

## Static Analysis
- Parse Python AST using `ast` module for structural analysis
- Count functions, classes, imports with `ast.NodeVisitor`
- Detect common anti-patterns: nested functions >3 levels, functions >50 lines

## Refactoring Strategies
- Extract method: identify repeated code blocks >3 lines
- Rename: use AST to find all references before renaming
- Move: check imports and cross-references before relocating code

## Test Generation
- Use `pytest` framework with descriptive test names
- Test edge cases: empty input, boundary values, type errors
- Mock external dependencies with `unittest.mock`

## Performance Analysis
- Profile with time complexity analysis (O notation)
- Identify hot loops and unnecessary re-computation
- Suggest caching with `functools.lru_cache` where applicable
