# Task: Multi-format Document Conversion

Convert three source files into a unified HTML report.

## Input Files

- `workspace/source/data.csv` - Tabular data (team member information)
- `workspace/source/notes.md` - Project notes in Markdown
- `workspace/source/config.json` - Project configuration

## Objective

Create `workspace/report.html` - a single HTML file that unifies all source content.

## Requirements

The HTML file must:
1. Be valid HTML with `<!DOCTYPE html>`, `<html>`, `<head>`, and `<body>` tags.
2. Have a `<title>` element in the head.
3. Include the CSV data as an HTML `<table>` with `<thead>` and `<tbody>`.
4. Include the Markdown content converted to HTML (headings, paragraphs, lists).
5. Include the JSON configuration rendered in a readable format (e.g., a definition list or structured section).
6. Use semantic HTML sections (`<section>`, `<h1>`/`<h2>`, etc.) to organize content.
