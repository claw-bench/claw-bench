# Task: Template Rendering

Render a Markdown template using data from a JSON file.

## Requirements

1. Read `workspace/template.md` and `workspace/data.json`.
2. The template uses Jinja2-style syntax:
   - Variables: `{{ variable_name }}` — replace with values from data.json.
   - Conditionals: `{% if condition %}...{% endif %}` — include content if the value is truthy.
   - Loops: `{% for item in list %}...{% endfor %}` — repeat content for each item.
   - Nested access: `{{ object.field }}` for nested data.
3. Render the template and write the result to `workspace/rendered.md`.
4. Remove any blank lines that result from removed conditional blocks, but preserve intentional blank lines between sections.

## Output

Save the rendered document to `workspace/rendered.md`.
