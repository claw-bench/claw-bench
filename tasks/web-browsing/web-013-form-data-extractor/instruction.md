# Task: Extract Form Structure from HTML

You are given a static HTML file at `workspace/form.html` containing multiple HTML forms. Extract the structure of each form.

## Requirements

1. Read `workspace/form.html`.
2. For each `<form>` element, extract:
   - **action**: The form's `action` attribute (empty string if not present).
   - **method**: The form's `method` attribute, uppercased (default to `"GET"` if not present).
   - **fields**: A list of input fields, each with:
     - **name**: The `name` attribute of the input/select/textarea element.
     - **type**: The `type` attribute (for `<input>`), `"select"` for `<select>`, or `"textarea"` for `<textarea>`. Default input type is `"text"`.
     - **required**: Boolean, `true` if the `required` attribute is present.
3. Only include fields that have a `name` attribute. Ignore submit buttons.
4. Produce a JSON array of form objects, in order of appearance.

## Output

Save the result to `workspace/forms.json`.
