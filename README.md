# Los números no cuadran
### Diagnostica discrepancias entre reportes con SQL y Python

Taller de **Datostada MX 2026** (Mérida). Dos reportes que deberían coincidir no coinciden: aprende un método para explicar por qué, demostrarlo con una consulta y convertirlo en una prueba automática para que no vuelva a pasar.

**Requisitos:** laptop, cuenta de Google y SQL básico (`SELECT`, `JOIN`, `GROUP BY`).

## Empieza aquí

| Cuaderno | Colab |
|---|---|
| 00 · Preparación | [![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jona866/taller-conciliacion-de-datos-datostada2026/blob/main/cuadernos/00_preparacion.ipynb) |
| 01 · Caso 1: el join que multiplica | [![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jona866/taller-conciliacion-de-datos-datostada2026/blob/main/cuadernos/01_caso1_join.ipynb) |
| 02 · Caso 2: zona horaria y definición | [![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jona866/taller-conciliacion-de-datos-datostada2026/blob/main/cuadernos/02_caso2_zona_horaria.ipynb) |
| 03 · Caso 3: el cierre de octubre (abierto) | [![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jona866/taller-conciliacion-de-datos-datostada2026/blob/main/cuadernos/03_caso3_abierto.ipynb) |
| 04 · El agente | [![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jona866/taller-conciliacion-de-datos-datostada2026/blob/main/cuadernos/04_agente.ipynb) |
| 05 · Pruebas automáticas | [![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jona866/taller-conciliacion-de-datos-datostada2026/blob/main/cuadernos/05_pruebas.ipynb) |

**En local:**
```bash
git clone https://github.com/jona866/taller-conciliacion-de-datos-datostada2026.git
cd taller-conciliacion-de-datos-datostada2026
pip install -r requirements.txt
python check_setup.py
jupyter lab cuadernos/
```

## El escenario
**Telar & Barro** es una tienda **ficticia** de artesanías yucatecas con venta en línea y tres sucursales (Mérida Centro, Valladolid y Progreso). Todos los nombres de personas y negocios son inventados. Los datos se generan con `python generar_datos.py` (determinista).

## El método
1. Confirmar y acotar · 2. Comparar definiciones · 3. Comparar en el mismo grano y contar filas antes y después de cada JOIN · 4. Partir el problema en dos · 5. Aislar los registros · 6. Explicar y demostrar con una consulta reproducible · 7. Volverlo prueba

Resumen de una página: [`docs/checklist.md`](docs/checklist.md)

## Contenido
```
cuadernos/      cuadernos para participantes (con pistas y verificación de respuestas)
soluciones/     los mismos cuadernos resueltos
datos/          CSV de cada caso + verificación (hash) de respuestas
sql/            el SQL real de cada reporte, con los comentarios de sus autores
tests/          pruebas automáticas (pytest) que nacen de los hallazgos
agente/         arnés de solo lectura para grabar un agente, evaluador y corridas
docs/           checklist, guía de facilitación y guion de diapositivas
nnc.py          utilidades: conectar, ver_sql, reporte, revisar, puente, probar
```

Pruebas: `NNC_DATOS=caso3 python -m pytest -q tests` (o `NNC_DATOS=carga_nueva`).
