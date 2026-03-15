# Task: Format CSV Data as Text Report

You are given a CSV file at `workspace/data.csv` containing product sales data. Produce a formatted text report.

## Requirements

1. Read `workspace/data.csv` which has columns: `product`, `quantity`, `price`.
2. Produce a text report (`workspace/report.txt`) with:
   - A title line: `Sales Report`
   - A blank line after the title.
   - A header row with the column names: `Product`, `Quantity`, `Price`, and `Total` (where Total = quantity * price).
   - A separator line using dashes (`-`).
   - One data row per CSV record with columns aligned (right-align numbers, left-align text). Use at least 2 spaces between columns.
   - A separator line using dashes (`-`).
   - A summary row showing `TOTAL` in the product column, the sum of all quantities, empty for price, and the grand total of all (quantity * price) values.
3. Write the result to `workspace/report.txt`.

## Example

For a CSV with:
```
product,quantity,price
Widget,10,2.50
```

The report would look like:
```
Sales Report

Product       Quantity    Price      Total
------------------------------------------------
Widget              10     2.50      25.00
------------------------------------------------
TOTAL               10               25.00
```

## Output

Save the report to `workspace/report.txt`.
