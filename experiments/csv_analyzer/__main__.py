"""Command-line interface for the sales CSV analyzer.

Usage:
    python -m experiments.csv_analyzer <path_to_csv>
"""

from __future__ import annotations

import argparse
import sys

from .analyzer import CsvAnalysisError, analyze_file


def _format_currency(value: float) -> str:
    return f"{value:,.2f}"


def render_report(result) -> str:
    """Build the human-readable summary of the analysis."""
    lines: list[str] = []
    lines.append("=" * 46)
    lines.append("SALES SUMMARY")
    lines.append("=" * 46)

    if not result.has_data:
        lines.append("No valid records were found to analyze.")
    else:
        lines.append(f"Records analyzed  : {result.record_count}")
        lines.append(f"Total revenue     : {_format_currency(result.total)}")
        lines.append("")
        lines.append("Revenue by category:")
        for categoria, total in sorted(
            result.by_category.items(), key=lambda item: item[1], reverse=True
        ):
            lines.append(f"  - {categoria}: {_format_currency(total)}")
        lines.append("")
        lines.append(
            "Top product by revenue: "
            f"{result.top_product} ({_format_currency(result.top_product_total)})"
        )

    if result.skipped_rows:
        lines.append("")
        lines.append(f"Rows skipped due to invalid data: {len(result.skipped_rows)}")
        for detalle in result.skipped_rows:
            lines.append(f"  ! {detalle}")

    lines.append("=" * 46)
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="csv_analyzer",
        description="Analyze a sales CSV file and display statistics.",
    )
    parser.add_argument("csv_path", help="Path to the sales CSV file.")
    args = parser.parse_args(argv)

    try:
        result = analyze_file(args.csv_path)
    except FileNotFoundError:
        print(f"Error: file not found: '{args.csv_path}'.", file=sys.stderr)
        return 2
    except CsvAnalysisError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(render_report(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
