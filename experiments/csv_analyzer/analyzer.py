"""Lógica de análisis de un CSV de ventas.

El CSV de entrada debe contener las columnas ``producto``, ``categoria``,
``cantidad`` y ``precio``. A partir de ellas se calcula el importe de cada
registro (``cantidad * precio``) y distintas estadísticas de facturación.

Solo se utiliza la biblioteca estándar de Python.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from typing import Iterable

REQUIRED_COLUMNS = ("producto", "categoria", "cantidad", "precio")


class CsvAnalysisError(Exception):
    """Error irrecuperable al procesar el CSV (por ejemplo, columnas faltantes)."""


@dataclass(frozen=True)
class SaleRecord:
    """Un registro válido de venta."""

    producto: str
    categoria: str
    cantidad: float
    precio: float

    @property
    def importe(self) -> float:
        """Importe del registro: cantidad x precio."""
        return self.cantidad * self.precio


@dataclass
class AnalysisResult:
    """Resultado del análisis de un conjunto de ventas."""

    record_count: int = 0
    total: float = 0.0
    by_category: dict[str, float] = field(default_factory=dict)
    top_product: str | None = None
    top_product_total: float = 0.0
    skipped_rows: list[str] = field(default_factory=list)

    @property
    def has_data(self) -> bool:
        """Indica si se procesó al menos un registro válido."""
        return self.record_count > 0


def _parse_number(raw: str) -> float:
    """Convierte un texto en número.

    Acepta separador decimal con punto o coma (por ejemplo ``"12,5"``).
    Lanza ``ValueError`` si el valor no es numérico.
    """
    text = (raw or "").strip()
    if not text:
        raise ValueError("valor vacío")
    try:
        return float(text)
    except ValueError:
        # Permite el uso de coma como separador decimal.
        if "," in text and "." not in text:
            return float(text.replace(",", "."))
        raise


def read_sales(path: str) -> tuple[list[SaleRecord], list[str]]:
    """Lee un CSV de ventas.

    Devuelve una tupla ``(registros_validos, filas_omitidas)``.

    - Si el archivo está vacío o no tiene cabecera, se devuelve una lista
      vacía de registros.
    - Si falta alguna de las columnas requeridas, se lanza
      ``CsvAnalysisError``.
    - Las filas con valores inválidos se omiten y se registran en
      ``filas_omitidas``.
    """
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        try:
            header = next(reader)
        except StopIteration:
            # Archivo completamente vacío.
            return [], []

        header = [column.strip().lower() for column in header]
        if not any(header):
            # Cabecera vacía (por ejemplo, solo una línea en blanco).
            return [], []

        missing = [column for column in REQUIRED_COLUMNS if column not in header]
        if missing:
            raise CsvAnalysisError(
                "Faltan columnas requeridas en el CSV: " + ", ".join(missing)
            )

        index = {column: header.index(column) for column in REQUIRED_COLUMNS}

        records: list[SaleRecord] = []
        skipped: list[str] = []

        for line_number, row in enumerate(reader, start=2):
            if not row or not any(cell.strip() for cell in row):
                continue  # Ignora líneas totalmente vacías.

            try:
                producto = row[index["producto"]].strip()
                categoria = row[index["categoria"]].strip()
                cantidad = _parse_number(row[index["cantidad"]])
                precio = _parse_number(row[index["precio"]])
                if not producto:
                    raise ValueError("producto vacío")
                if not categoria:
                    raise ValueError("categoría vacía")
            except (IndexError, ValueError) as exc:
                skipped.append(f"línea {line_number}: {exc}")
                continue

            records.append(
                SaleRecord(
                    producto=producto,
                    categoria=categoria,
                    cantidad=cantidad,
                    precio=precio,
                )
            )

        return records, skipped


def analyze_rows(records: Iterable[SaleRecord], skipped: list[str] | None = None) -> AnalysisResult:
    """Calcula las estadísticas de facturación a partir de los registros."""
    result = AnalysisResult(skipped_rows=list(skipped or []))
    product_totals: dict[str, float] = {}

    for record in records:
        importe = record.importe
        result.record_count += 1
        result.total += importe
        result.by_category[record.categoria] = (
            result.by_category.get(record.categoria, 0.0) + importe
        )
        product_totals[record.producto] = (
            product_totals.get(record.producto, 0.0) + importe
        )

    if product_totals:
        # Mayor facturación; en caso de empate, nombre alfabéticamente menor.
        top_product = sorted(
            product_totals, key=lambda name: (-product_totals[name], name)
        )[0]
        result.top_product = top_product
        result.top_product_total = product_totals[top_product]

    return result


def analyze_file(path: str) -> AnalysisResult:
    """Lee y analiza un archivo CSV de ventas en un solo paso."""
    records, skipped = read_sales(path)
    return analyze_rows(records, skipped)
