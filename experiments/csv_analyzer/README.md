# Analizador de datos CSV

Aplicación de línea de comandos en Python 3 (solo biblioteca estándar) para
analizar archivos CSV con información de ventas y generar estadísticas.

## Requisitos

- Python 3.10 o superior.
- No requiere instalar dependencias adicionales.

## Formato del CSV

El archivo debe incluir la cabecera con las columnas `producto`, `categoria`,
`cantidad` y `precio`:

```csv
producto,categoria,cantidad,precio
Laptop,Electronica,3,1200.00
Mouse,Electronica,10,25.50
```

Los encabezados no distinguen mayúsculas/minúsculas ni espacios sobrantes.
El separador decimal puede ser punto o coma.

## Uso

Desde la raíz del repositorio:

```bash
python -m experiments.csv_analyzer experiments/csv_analyzer/ventas.csv
```

Salida de ejemplo:

```
==============================================
RESUMEN DE VENTAS
==============================================
Registros analizados : 7
Facturación total    : 8,075.00

Facturación por categoría:
  - Electronica: 6,255.00
  - Muebles: 1,200.00
  - Ropa: 620.00

Producto con mayor facturación: Laptop (6,000.00)
==============================================
```

## Cálculos

- **Importe de cada registro**: `cantidad * precio`.
- **Facturación total**: suma de todos los importes.
- **Facturación por categoría**: suma agrupada por `categoria`.
- **Producto con mayor facturación**: mayor importe acumulado por `producto`
  (en caso de empate se elige el nombre alfabéticamente menor).

## Manejo de errores

- **Archivo vacío o solo cabecera**: se informa que no hay registros válidos.
- **Columnas requeridas faltantes**: se muestra un error y el programa termina
  con código de salida `1`.
- **Archivo inexistente**: se muestra un error y el programa termina con código
  de salida `2`.
- **Valores inválidos** (números no numéricos, campos vacíos): la fila se omite
  y se reporta en el resumen.

## Pruebas automatizadas

Las pruebas usan `unittest` y están en
`experiments/csv_analyzer/tests/test_analyzer.py`.

Desde la raíz del repositorio:

```bash
python -m unittest discover -s experiments/csv_analyzer/tests -t .
```

O directamente:

```bash
python experiments/csv_analyzer/tests/test_analyzer.py
```
