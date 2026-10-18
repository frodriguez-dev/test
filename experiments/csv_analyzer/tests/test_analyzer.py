"""Automated tests for the sales CSV analyzer."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest

# Ensure the repository root is on sys.path regardless of where the tests run.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)
))))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from experiments.csv_analyzer.analyzer import (  # noqa: E402
    CsvAnalysisError,
    SaleRecord,
    analyze_rows,
    read_sales,
)

SAMPLE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ventas.csv"
)


def _write_temp_csv(content: str) -> str:
    handle = tempfile.NamedTemporaryFile(
        "w", suffix=".csv", delete=False, encoding="utf-8"
    )
    handle.write(content)
    handle.close()
    return handle.name


class SaleRecordTests(unittest.TestCase):
    def test_importe_is_cantidad_times_precio(self):
        record = SaleRecord("Laptop", "Electronica", 3, 1200.0)
        self.assertEqual(record.importe, 3600.0)


class AnalyzeSampleFileTests(unittest.TestCase):
    def test_total_revenue(self):
        records, skipped = read_sales(SAMPLE_PATH)
        result = analyze_rows(records, skipped)
        self.assertEqual(result.record_count, 7)
        self.assertAlmostEqual(result.total, 8075.0)
        self.assertEqual(result.skipped_rows, [])

    def test_revenue_by_category(self):
        result = analyze_rows(*read_sales(SAMPLE_PATH))
        self.assertAlmostEqual(result.by_category["Electronica"], 6255.0)
        self.assertAlmostEqual(result.by_category["Muebles"], 1200.0)
        self.assertAlmostEqual(result.by_category["Ropa"], 620.0)

    def test_top_product_by_revenue(self):
        result = analyze_rows(*read_sales(SAMPLE_PATH))
        self.assertEqual(result.top_product, "Laptop")
        self.assertAlmostEqual(result.top_product_total, 6000.0)


class EmptyAndInvalidInputTests(unittest.TestCase):
    def test_empty_file(self):
        path = _write_temp_csv("")
        try:
            records, skipped = read_sales(path)
            result = analyze_rows(records, skipped)
            self.assertEqual(records, [])
            self.assertFalse(result.has_data)
            self.assertEqual(result.total, 0.0)
            self.assertIsNone(result.top_product)
        finally:
            os.remove(path)

    def test_header_only(self):
        path = _write_temp_csv("producto,categoria,cantidad,precio\n")
        try:
            result = analyze_rows(*read_sales(path))
            self.assertFalse(result.has_data)
            self.assertEqual(result.total, 0.0)
        finally:
            os.remove(path)

    def test_missing_columns(self):
        path = _write_temp_csv("producto,cantidad\nLaptop,3\n")
        try:
            with self.assertRaises(CsvAnalysisError):
                read_sales(path)
        finally:
            os.remove(path)

    def test_invalid_values_are_skipped(self):
        content = (
            "producto,categoria,cantidad,precio\n"
            "Laptop,Electronica,3,1200.00\n"
            "Mouse,Electronica,abc,25.50\n"
            "Silla,Muebles,4,\n"
            "Mesa,Muebles,2,300.00\n"
        )
        path = _write_temp_csv(content)
        try:
            records, skipped = read_sales(path)
            result = analyze_rows(records, skipped)
            self.assertEqual(result.record_count, 2)
            self.assertEqual(len(result.skipped_rows), 2)
            self.assertAlmostEqual(result.total, 4200.0)
        finally:
            os.remove(path)

    def test_comma_as_decimal_separator(self):
        content = (
            "producto,categoria,cantidad,precio\n"
            'Tornillo,Ferreteria,100,"0,25"\n'
        )
        path = _write_temp_csv(content)
        try:
            records, skipped = read_sales(path)
            result = analyze_rows(records, skipped)
            self.assertEqual(result.record_count, 1)
            self.assertAlmostEqual(result.total, 25.0)
        finally:
            os.remove(path)

    def test_tie_breaks_on_alphabetical_name(self):
        records = [
            SaleRecord("Zeta", "Cat", 1, 100.0),
            SaleRecord("Alfa", "Cat", 1, 100.0),
        ]
        result = analyze_rows(records)
        self.assertEqual(result.top_product, "Alfa")


if __name__ == "__main__":
    unittest.main()
