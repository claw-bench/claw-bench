# Coding Standards

## 1. Naming Conventions (NAM)
- **NAM-01**: Use `snake_case` for functions and variables
- **NAM-02**: Use `PascalCase` only for class names
- **NAM-03**: Constants must be `UPPER_SNAKE_CASE` and defined at module level
- **NAM-04**: No single-letter variable names except in comprehensions and short lambdas
- **NAM-05**: Method names should clearly describe their action (e.g., `to_dict()` not `getData()`)

## 2. Error Handling (ERR)
- **ERR-01**: All database operations must be wrapped in try/except blocks
- **ERR-02**: Never use bare `except:` clauses; always catch specific exceptions
- **ERR-03**: HTTP endpoints must return appropriate status codes for all paths
- **ERR-04**: File operations must use context managers (`with` statement)
- **ERR-05**: Always validate and sanitize user input before processing

## 3. Security (SEC)
- **SEC-01**: Never use string formatting/concatenation to build SQL queries; use parameterized queries or ORM
- **SEC-02**: Never hardcode secrets, passwords, API keys, or connection strings in source code
- **SEC-03**: Never use `eval()`, `exec()`, `pickle.loads()` on untrusted input
- **SEC-04**: Never use `subprocess` with `shell=True`
- **SEC-05**: Always validate file paths to prevent path traversal attacks
- **SEC-06**: Use strong hashing algorithms (bcrypt, argon2, scrypt) for passwords; never MD5 or plain SHA-256
- **SEC-07**: Never store or expose sensitive PII (SSN, credit card numbers) without encryption
- **SEC-08**: SSL/TLS verification must never be disabled (`verify=False`)
- **SEC-09**: Authentication tokens and session data must not be stored in client-accessible cookies without signing
- **SEC-10**: Never trust client-side values for authorization decisions

## 4. Documentation (DOC)
- **DOC-01**: All public functions must have docstrings
- **DOC-02**: All modules must have a module-level docstring
- **DOC-03**: Complex logic must have inline comments explaining the reasoning
- **DOC-04**: Type hints are required for all function parameters and return types

## 5. Performance (PERF)
- **PERF-01**: Avoid N+1 query patterns; use eager loading or batch queries
- **PERF-02**: Do not import modules inside functions unless there is a lazy-loading reason
- **PERF-03**: Use list comprehensions over manual loop-append patterns where appropriate

## 6. Style (STY)
- **STY-01**: Maximum function length is 20 lines (excluding docstring and blank lines)
- **STY-02**: Maximum cyclomatic complexity per function is 8
- **STY-03**: Imports must be at the top of the file, organized: stdlib, third-party, local
- **STY-04**: No unused imports
- **STY-05**: Consistent return types within a function
