# Task: SVG Bar Chart Generator

You are given a JSON file at `workspace/chart_data.json` containing an array of objects, each with `"label"` and `"value"` keys. Generate an SVG bar chart from this data.

## Requirements

1. Read `workspace/chart_data.json`.
2. Produce `workspace/chart.svg` containing a valid SVG bar chart.
3. The SVG must include:
   - An `<svg>` root element with `xmlns="http://www.w3.org/2000/svg"`.
   - A chart title rendered as a `<text>` element containing the text "Sales by Region".
   - One `<rect>` element per data point representing a bar.
   - One `<text>` element per data point containing the label.
   - Bars should have heights proportional to their values.
4. Each bar's `<rect>` must have a `height` attribute that is proportional to its `value`.
5. Labels must appear as `<text>` elements and include the exact label strings from the data.

## Output

Save the result to `workspace/chart.svg`.
