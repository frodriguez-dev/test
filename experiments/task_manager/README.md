# Gestor de tareas por consola

Aplicación de línea de comandos escrita en Python que permite gestionar tareas
personales y persistirlas automáticamente en un archivo JSON.

Usa **exclusivamente la biblioteca estándar** de Python (no requiere instalar
dependencias).

## Requisitos

- Python 3.10 o superior.

## Estructura

```
experiments/task_manager/
├── __init__.py              # Exporta las clases públicas
├── __main__.py              # Permite ejecutar con python -m
├── cli.py                   # Interfaz de línea de comandos (argparse)
├── task_manager.py          # Lógica de tareas y persistencia en JSON
├── README.md
└── tests/
    └── test_task_manager.py # Pruebas unitarias con unittest
```

## Uso

Ejecuta la aplicación como módulo desde la raíz del repositorio:

```bash
python -m experiments.task_manager <comando> [opciones]
```

### Comandos disponibles

| Comando    | Descripción                              |
| ---------- | ---------------------------------------- |
| `add`      | Crea una tarea nueva.                    |
| `list`     | Lista todas las tareas con su estado.    |
| `complete` | Marca una tarea como completada.         |
| `delete`   | Elimina una tarea.                       |

Opciones globales:

- `--file RUTA`: ruta del archivo JSON de tareas (por defecto `tasks.json`).

### Ejemplos

Crear una tarea con descripción opcional:

```bash
python -m experiments.task_manager add "Comprar pan" -d "Integral"
# Tarea creada:   1 [ ] Comprar pan  (integral)

python -m experiments.task_manager add "Estudiar Python"
# Tarea creada:   2 [ ] Estudiar Python
```

Listar las tareas (el estado se muestra como `[ ]` pendiente y `[x]` completada):

```bash
python -m experiments.task_manager list
#   1 [ ] Comprar pan  (integral)
#   2 [ ] Estudiar Python
```

Marcar una tarea como completada:

```bash
python -m experiments.task_manager complete 1
# Tarea completada:   1 [x] Comprar pan  (integral)
```

Eliminar una tarea:

```bash
python -m experiments.task_manager delete 2
# Tarea eliminada:   2 [ ] Estudiar Python
```

Usar un archivo de almacenamiento distinto:

```bash
python -m experiments.task_manager --file mis_tareas.json list
```

### Manejo de errores

- Un ID inexistente muestra un mensaje de error y devuelve el código de salida
  `1`:

  ```bash
  python -m experiments.task_manager complete 99
  # Error: No existe una tarea con el ID 99.
  ```

- Un título vacío en `add` también finaliza con un error.
- Argumentos inválidos (por ejemplo, un ID no numérico) son rechazados por
  `argparse` con un mensaje de uso.

## Persistencia

Las tareas se guardan automáticamente tras cada operación que modifica el estado
(`add`, `complete`, `delete`) en el archivo JSON indicado (por defecto
`tasks.json`). Al volver a ejecutar la aplicación, las tareas se cargan desde ese
archivo.

Formato del archivo:

```json
[
  {
    "id": 1,
    "title": "Comprar pan",
    "description": "Integral",
    "completed": true
  }
]
```

> El archivo `tasks.json` es un artefacto generado en tiempo de ejecución y no
> debería versionarse.

## Pruebas

Las pruebas usan `unittest` de la biblioteca estándar. Ejecútalas desde la raíz
del repositorio:

```bash
python -m unittest discover -s experiments/task_manager/tests -v
```

También puedes ejecutar el archivo de pruebas directamente:

```bash
python experiments/task_manager/tests/test_task_manager.py
```
