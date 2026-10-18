# CSV Data Analyzer

A Python 3 command-line application (standard library only) to analyze CSV
files with sales information and produce statistics.

## Requirements

- Python 3.10 or higher.
- No additional dependencies are required.

## CSV format

The file must include a header with the `producto`, `categoria`, `cantidad`
and `precio` columns:

```csv
producto,categoria,cantidad,precio
Laptop,Electronica,3,1200.00
Mouse,Electronica,10,25.50
```

Header matching is case-insensitive and ignores surrounding whitespace.
The decimal separator may be a dot or a comma.

## Usage

From the repository root:

```bash
python -m experiments.csv_analyzer experiments/csv_analyzer/ventas.csv
```

Sample output:

```
==============================================
SALES SUMMARY
==============================================
Records analyzed  : 7
Total revenue     : 8,075.00

Revenue by category:
  - Electronica: 6,255.00
  - Muebles: 1,200.00
  - Ropa: 620.00

Top product by revenue: Laptop (6,000.00)
==============================================
```

## Calculations

- **Amount per record**: `cantidad * precio`.
- **Total revenue**: sum of all amounts.
- **Revenue by category**: sum grouped by `categoria`.
- **Top product by revenue**: the highest accumulated amount per `producto`
  (on a tie, the alphabetically smallest name is chosen).

## Error handling

- **Empty file or header only**: it reports that there are no valid records.
- **Missing required columns**: an error is displayed and the program exits
  with status code `1`.
- **Nonexistent file**: an error is displayed and the program exits with
  status code `2`.
- **Invalid values** (non-numeric numbers, empty fields): the row is skipped
  and reported in the summary.

## Automated tests

The tests use `unittest` and live in
`experiments/csv_analyzer/tests/test_analyzer.py`.

From the repository root:

```bash
python -m unittest discover -s experiments/csv_analyzer/tests -t .
```

Or directly:

```bash
python experiments/csv_analyzer/tests/test_analyzer.py
```
