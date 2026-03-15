# Task: Form Field Inventory

Analyze an HTML form and produce a complete inventory of all form fields.

## Requirements

1. Read `workspace/form.html`.
2. Find all form fields (`<input>`, `<select>`, `<textarea>`).
3. For each field, extract:
   - `name`: the name attribute.
   - `type`: the type (text, email, password, select, textarea, checkbox, radio, etc.).
   - `required`: boolean, whether the field has the `required` attribute.
   - `label`: text of the associated `<label>` element (if any).
   - `validation`: object with any validation attributes found (`minlength`, `maxlength`, `pattern`, `min`, `max`). Empty object if none.
4. Write to `workspace/form_fields.json` as an array of field objects.

## Output

Save the form field inventory to `workspace/form_fields.json`.
