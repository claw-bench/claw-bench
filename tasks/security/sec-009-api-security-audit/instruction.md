# Task: Audit OpenAPI Specification for Security Issues

Analyze `workspace/api_spec.json` (an OpenAPI 3.0 specification) for security issues.

## Requirements

1. Read `workspace/api_spec.json`.
2. Check each endpoint for:
   - **Authentication**: Missing or optional security requirements
   - **Rate limiting**: Absence of rate limit headers/configuration
   - **Input validation**: Missing parameter constraints (type, min/max, pattern)
   - **CORS**: Overly permissive CORS configuration
   - **PII exposure**: Endpoints that return sensitive personal data without filtering
   - **Authorization**: Missing role-based access controls
   - **HTTP methods**: Dangerous methods without protection
3. Write `workspace/api_audit.json` as a JSON array of objects, each with:
   - `endpoint`: the path and method (e.g., `"GET /users"`)
   - `category`: one of `"authentication"`, `"rate_limiting"`, `"input_validation"`, `"cors"`, `"pii_exposure"`, `"authorization"`, `"http_methods"`
   - `description`: explanation of the security issue
   - `severity`: `"critical"`, `"high"`, `"medium"`, or `"low"`
   - `recommendation`: how to fix the issue

## Notes

- The API spec has 10 endpoints with 7 security issues total.
- Some endpoints are properly secured; do not flag those.

## Output

Save results to `workspace/api_audit.json`.
