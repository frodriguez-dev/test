"""Analysis logic for a sales CSV file.

The input CSV must contain the columns ``producto``, ``categoria``,
``cantidad`` and ``precio``. From them, the amount of each record is computed
(``cantidad * precio``) along with several revenue statistics.

Only the Python standard library is used.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from typing import Iterable

REQUIRED_COLUMNS = ("producto", "categoria", "cantidad", "precio")


class CsvAnalysisError(Exception):
    """Unrecoverable error while processing the CSV (e.g. missing columns)."""


@dataclass(frozen=True)
class SaleRecord:
    """A valid sales record."""

    producto: str
    categoria: str
    cantidad: float
    precio: float

    @property
    def importe(self) -> float:
        """Record amount: cantidad x precio."""
        return self.cantidad * self.precio


@dataclass
class AnalysisResult:
    """Result of analyzing a set of sales records."""

    record_count: int = 0
    total: float = 0.0
    by_category: dict[str, float] = field(default_factory=dict)
    top_product: str | None = None
    top_product_total: float = 0.0
    skipped_rows: list[str] = field(default_factory=list)

    @property
    def has_data(self) -> bool:
        """Whether at least one valid record was processed."""
        return self.record_count > 0


def _parse_number(raw: str) -> float:
    """Convert text into a number.

    Accepts a decimal separator using a dot or a comma (for example ``"12,5"``).
    Raises ``ValueError`` if the value is not numeric.
    """
    text = (raw or "").strip()
    if not text:
        raise ValueError("empty value")
    try:
        return float(text)
    except ValueError:
        # Allow a comma as the decimal separator.
        if "," in text and "." not in text:
            return float(text.replace(",", "."))
        raise


def read_sales(path: str) -> tuple[list[SaleRecord], list[str]]:
    """Read a sales CSV file.

    Returns a tuple ``(valid_records, skipped_rows)``.

    - If the file is empty or has no header, an empty list of records is
      returned.
    - If any required column is missing, ``CsvAnalysisError`` is raised.
    - Rows with invalid values are skipped and recorded in ``skipped_rows``.
    """
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        try:
            header = next(reader)
        except StopIteration:
            # Completely empty file.
            return [], []

        header = [column.strip().lower() for column in header]
        if not any(header):
            # Empty header (for example, a single blank line).
            return [], []

        missing = [column for column in REQUIRED_COLUMNS if column not in header]
        if missing:
            raise CsvAnalysisError(
                "Missing required columns in the CSV: " + ", ".join(missing)
            )

        index = {column: header.index(column) for column in REQUIRED_COLUMNS}

        records: list[SaleRecord] = []
        skipped: list[str] = []

        for line_number, row in enumerate(reader, start=2):
            if not row or not any(cell.strip() for cell in row):
                continue  # Ignore fully blank lines.

            try:
                producto = row[index["producto"]].strip()
                categoria = row[index["categoria"]].strip()
                cantidad = _parse_number(row[index["cantidad"]])
                precio = _parse_number(row[index["precio"]])
                if not producto:
                    raise ValueError("empty product")
                if not categoria:
                    raise ValueError("empty category")
            except (IndexError, ValueError) as exc:
                skipped.append(f"line {line_number}: {exc}")
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
    """Compute revenue statistics from the given records."""
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
        # Highest revenue; on a tie, the alphabetically smallest name.
        top_product = sorted(
            product_totals, key=lambda name: (-product_totals[name], name)
        )[0]
        result.top_product = top_product
        result.top_product_total = product_totals[top_product]

    return result


def analyze_file(path: str) -> AnalysisResult:
    """Read and analyze a sales CSV file in a single step."""
    records, skipped = read_sales(path)
    return analyze_rows(records, skipped)
