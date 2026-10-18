"""Interfaz de línea de comandos del analizador de CSV de ventas.

Uso:
    python -m experiments.csv_analyzer <ruta_al_csv>
"""

from __future__ import annotations

import argparse
import sys

from .analyzer import CsvAnalysisError, analyze_file


def _format_currency(value: float) -> str:
    return f"{value:,.2f}"


def render_report(result) -> str:
    """Construye el resumen legible del análisis."""
    lines: list[str] = []
    lines.append("=" * 46)
    lines.append("RESUMEN DE VENTAS")
    lines.append("=" * 46)

    if not result.has_data:
        lines.append("No se encontraron registros válidos para analizar.")
    else:
        lines.append(f"Registros analizados : {result.record_count}")
        lines.append(f"Facturación total    : {_format_currency(result.total)}")
        lines.append("")
        lines.append("Facturación por categoría:")
        for categoria, total in sorted(
            result.by_category.items(), key=lambda item: item[1], reverse=True
        ):
            lines.append(f"  - {categoria}: {_format_currency(total)}")
        lines.append("")
        lines.append(
            "Producto con mayor facturación: "
            f"{result.top_product} ({_format_currency(result.top_product_total)})"
        )

    if result.skipped_rows:
        lines.append("")
        lines.append(f"Filas omitidas por datos inválidos: {len(result.skipped_rows)}")
        for detalle in result.skipped_rows:
            lines.append(f"  ! {detalle}")

    lines.append("=" * 46)
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="csv_analyzer",
        description="Analiza un archivo CSV de ventas y muestra estadísticas.",
    )
    parser.add_argument("csv_path", help="Ruta al archivo CSV de ventas.")
    args = parser.parse_args(argv)

    try:
        result = analyze_file(args.csv_path)
    except FileNotFoundError:
        print(f"Error: no se encontró el archivo '{args.csv_path}'.", file=sys.stderr)
        return 2
    except CsvAnalysisError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(render_report(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
