"""CSV sales data analyzer.

Exposes the main logic to read a sales CSV file and compute revenue
statistics using only the standard library.
"""

from .analyzer import (
    AnalysisResult,
    CsvAnalysisError,
    SaleRecord,
    analyze_file,
    analyze_rows,
    read_sales,
)

__all__ = [
    "AnalysisResult",
    "CsvAnalysisError",
    "SaleRecord",
    "analyze_file",
    "analyze_rows",
    "read_sales",
]
