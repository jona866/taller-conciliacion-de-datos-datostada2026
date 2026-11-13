"""
Verifica que tu entorno está listo para el taller.

    python check_setup.py        (local)
    import check_setup; check_setup.main()   (Colab / Jupyter)
"""
from __future__ import annotations

import importlib
import json
import platform
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent


def _ok(nombre, bien, detalle=""):
    print(f"{'✅' if bien else '❌'} {nombre:<38} {detalle}")
    return bien


def main() -> bool:
    print(f"Python {platform.python_version()} · {platform.system()}\n")
    resultados = []
    resultados.append(_ok("Python 3.9 o superior", sys.version_info >= (3, 9), platform.python_version()))

    for mod, minimo in [("duckdb", (1, 1)), ("pandas", (1, 5))]:
        try:
            m = importlib.import_module(mod)
            v = tuple(int(x) for x in m.__version__.split(".")[:2])
            resultados.append(_ok(f"{mod} {'.'.join(map(str, minimo))}+", v >= minimo, m.__version__))
        except ImportError:
            resultados.append(_ok(mod, False, "no instalado: pip install -r requirements.txt"))
    for mod in ["pytest"]:
        try:
            m = importlib.import_module(mod)
            resultados.append(_ok(mod, True, m.__version__))
        except ImportError:
            resultados.append(_ok(mod, False, "no instalado (solo se usa en el bloque de pruebas)"))

    manifiesto = json.loads((RAIZ / "datos" / "manifiesto.json").read_text(encoding="utf-8"))
    faltan = []
    for rel, filas in manifiesto.items():
        f = RAIZ / "datos" / rel
        if not f.exists():
            faltan.append(rel)
            continue
        with open(f, encoding="utf-8") as fh:
            if sum(1 for _ in fh) - 1 != filas:
                faltan.append(rel + " (filas distintas)")
    resultados.append(_ok("Datos de los casos", not faltan, f"{len(manifiesto)} archivos" if not faltan else ", ".join(faltan[:3])))

    try:
        import duckdb
        con = duckdb.connect()
        con.execute("SET TimeZone='UTC'")
        r = con.execute("SELECT CAST((TIMESTAMP '2026-11-01 02:14:09' AT TIME ZONE 'UTC') "
                        "AT TIME ZONE 'America/Merida' AS VARCHAR)").fetchone()[0]
        resultados.append(_ok("Zonas horarias en DuckDB", r.startswith("2026-10-31 20:14:09"), r))
    except Exception as e:  # noqa: BLE001
        resultados.append(_ok("Zonas horarias en DuckDB", False, str(e)[:80]))

    try:
        sys.path.insert(0, str(RAIZ))
        import nnc
        con = nnc.conectar("caso1")
        dif = nnc.total(con, "caso1_dashboard_ventas") - nnc.total(con, "caso1_reporte_finanzas")
        resultados.append(_ok("Reportes del caso 1", dif != 0, "se reproducen las dos cifras"))
    except Exception as e:  # noqa: BLE001
        resultados.append(_ok("Reportes del caso 1", False, str(e)[:80]))

    print()
    if all(resultados):
        print("🎉 Todo listo. Nos vemos en el taller.")
    else:
        print("⚠️ Algo falta. Revisa las líneas con ❌ o pide ayuda al facilitador.")
    return all(resultados)


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
