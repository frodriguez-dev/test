"""Analizador de datos CSV de ventas.

Expone la lógica principal para leer un CSV de ventas y calcular
estadísticas de facturación usando únicamente la biblioteca estándar.
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
