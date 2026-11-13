"""
Utilidades del taller "Los números no cuadran".

    import nnc
    con = nnc.conectar("caso1")          # DuckDB en memoria con las tablas del caso
    nnc.q(con, "SELECT COUNT(*) FROM pedidos")
    nnc.ver_sql("caso1_dashboard_ventas")  # muestra el SQL real del reporte
    nnc.reporte(con, "caso1_dashboard_ventas")
    nnc.revisar("caso1.diferencia", 12345.67)   # compara tu respuesta sin revelar la solución
"""
from __future__ import annotations

import hashlib
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import duckdb

RAIZ = Path(__file__).resolve().parent
DATOS = RAIZ / "datos"
SQL = RAIZ / "sql"

# Parámetros de cada conjunto de datos (periodo del reporte y hora de corte de finanzas)
PARAMETROS = {
    "caso1": dict(desde="2026-08-01", hasta="2026-08-31"),
    "caso2": dict(desde="2026-10-01", hasta="2026-10-31"),
    "caso3": dict(desde="2026-10-01", hasta="2026-10-31", corte="2026-11-03 09:00:00"),
    "carga_nueva": dict(desde="2026-11-01", hasta="2026-11-08", corte="2026-11-09 09:00:00"),
}

# Tipos de cada columna, tal como los define el equipo de datos
TIPOS = {
    "pedidos": {"pedido_id": "VARCHAR", "cliente_id": "VARCHAR", "canal": "VARCHAR", "sucursal": "VARCHAR",
                "fecha_pedido": "TIMESTAMP", "estatus": "VARCHAR",
                "fecha_pedido_local": "TIMESTAMP", "total": "DECIMAL(12,2)", "cargado_en": "TIMESTAMP"},
    "lineas_pedido": {"linea_id": "INTEGER", "pedido_id": "VARCHAR", "producto_id": "INTEGER",
                      "cantidad": "INTEGER", "precio_unitario": "DECIMAL(12,2)"},
    "pagos": {"pago_id": "VARCHAR", "pedido_id": "VARCHAR", "metodo": "VARCHAR", "monto": "DECIMAL(12,2)",
              "pagado_en": "TIMESTAMPTZ"},
    "devoluciones": {"devolucion_id": "VARCHAR", "pedido_id": "VARCHAR", "fecha_devolucion": "DATE",
                     "motivo": "VARCHAR", "monto": "DECIMAL(12,2)"},
    "productos": {"producto_id": "INTEGER", "sku": "VARCHAR", "nombre": "VARCHAR", "categoria": "VARCHAR",
                  "precio_lista": "DECIMAL(12,2)"},
    "clientes": {"cliente_id": "VARCHAR", "nombre": "VARCHAR", "segmento": "VARCHAR", "ciudad": "VARCHAR",
                 "fecha_alta": "DATE", "cargado_en": "TIMESTAMP"},
    "pasarela_cobros": {"cobro_id": "VARCHAR", "referencia": "VARCHAR", "monto": "BIGINT", "moneda": "VARCHAR",
                        "estado": "VARCHAR", "cobrado_en": "TIMESTAMPTZ"},
    "caja_sucursal": {"ticket_id": "VARCHAR", "pedido_id": "VARCHAR", "sucursal": "VARCHAR",
                      "importe": "DECIMAL(12,2)", "fecha_hora": "TIMESTAMP", "recibido_en": "TIMESTAMP"},
    "cargas": {"carga_id": "INTEGER", "fuente": "VARCHAR", "sucursal": "VARCHAR", "recibido_en": "TIMESTAMP",
               "filas": "INTEGER"},
}


def conectar(caso: str, zona_horaria: str = "UTC") -> duckdb.DuckDBPyConnection:
    """Crea una base DuckDB en memoria con las tablas del caso.

    La zona horaria de la sesión se fija en UTC a propósito, igual que un servidor,
    para que todos obtengan el mismo resultado en Colab y en su laptop.
    """
    carpeta = DATOS / caso
    if not carpeta.exists():
        raise FileNotFoundError(f"No encuentro {carpeta}. ¿Ejecutaste la celda de preparación?")
    con = duckdb.connect()
    con.execute(f"SET TimeZone = '{zona_horaria}'")
    for archivo in sorted(carpeta.glob("*.csv")):
        tabla = archivo.stem
        with open(archivo, encoding="utf-8") as f:
            columnas = f.readline().strip().split(",")
        tipos = {c: TIPOS.get(tabla, {}).get(c, "VARCHAR") for c in columnas}
        tipos_sql = "{" + ", ".join(f"'{c}': '{t}'" for c, t in tipos.items()) + "}"
        con.execute(f"""CREATE TABLE {tabla} AS
                        SELECT * FROM read_csv('{archivo.as_posix()}', header=true, columns={tipos_sql})""")
    return con


def q(con, sql: str):
    """Ejecuta una consulta y regresa un DataFrame de pandas."""
    return con.execute(sql).df()


def _sql(nombre: str, caso: str | None = None) -> str:
    texto = (SQL / f"{nombre}.sql").read_text(encoding="utf-8")
    caso = caso or nombre.split("_")[0]
    for k, v in PARAMETROS.get(caso, {}).items():
        texto = texto.replace("{" + k + "}", v)
    return texto


def ver_sql(nombre: str, caso: str | None = None):
    """Imprime el SQL del reporte con sus parámetros."""
    print(_sql(nombre, caso))


def reporte(con, nombre: str, caso: str | None = None):
    """Ejecuta el SQL de un reporte y regresa el DataFrame."""
    return con.execute(_sql(nombre, caso)).df()


def total(con, nombre: str, caso: str | None = None) -> Decimal:
    """Total de un reporte (suma de la última columna)."""
    df = reporte(con, nombre, caso)
    return Decimal(str(df.iloc[:, -1].sum())).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _normaliza(valor):
    if isinstance(valor, bool):
        return str(valor)
    if isinstance(valor, int):
        return str(valor)
    if isinstance(valor, (float, Decimal)):
        return f"{Decimal(str(valor)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP):.2f}"
    try:  # numpy y similares
        import numbers
        if isinstance(valor, numbers.Integral):
            return str(int(valor))
        if isinstance(valor, numbers.Real):
            return _normaliza(float(valor))
    except Exception:
        pass
    return str(valor)


def revisar(clave: str, valor) -> bool:
    """Compara tu respuesta con la esperada sin mostrar la solución."""
    esperado = json.loads((DATOS / "verificacion.json").read_text(encoding="utf-8"))
    if clave not in esperado:
        print(f"No conozco la clave '{clave}'. Claves de este caso: "
              + ", ".join(k for k in esperado if k.startswith(clave.split('.')[0])))
        return False
    texto = _normaliza(valor)
    ok = hashlib.sha256(texto.encode()).hexdigest()[:16] == esperado[clave]
    print(("✅ Correcto: " if ok else "❌ Todavía no: ") + f"{clave} = {texto}")
    return ok


def puente(partidas: dict, diferencia) -> None:
    """Imprime un puente de conciliación y su residuo."""
    dif = Decimal(_normaliza(diferencia))
    suma = Decimal("0")
    print(f"{'Causa':<50}{'Monto':>16}")
    print("-" * 66)
    for causa, monto in partidas.items():
        m = Decimal(_normaliza(monto))
        suma += m
        print(f"{causa:<50}{m:>16,.2f}")
    print("-" * 66)
    print(f"{'Total explicado':<50}{suma:>16,.2f}")
    print(f"{'Diferencia entre reportes':<50}{dif:>16,.2f}")
    residuo = dif - suma
    print(f"{'Residuo':<50}{residuo:>16,.2f}")
    print("✅ Todo explicado." if residuo == 0 else "⚠️ Hay residuo: falta al menos una causa (o sobra una).")


def revisar_hallazgo(caso: str, monto) -> bool:
    """Caso abierto: dice si un monto coincide con alguna causa sembrada, sin decir cuál."""
    esperado = json.loads((DATOS / "verificacion.json").read_text(encoding="utf-8"))
    texto = _normaliza(monto)
    h = hashlib.sha256(texto.encode()).hexdigest()[:16]
    h_abs = hashlib.sha256(texto.lstrip("-").encode()).hexdigest()[:16]
    total = len(esperado.get(f"{caso}.hallazgos", []))
    if h in esperado.get(f"{caso}.hallazgos", []):
        print(f"✅ {texto} coincide con una de las {total} causas sembradas.")
        return True
    if h_abs in esperado.get(f"{caso}.hallazgos_abs", []):
        print(f"🟡 {texto}: el monto coincide, pero revisa el signo (efecto sobre comercial − finanzas).")
        return False
    print(f"❌ {texto} no coincide con ninguna causa. Puede ser una combinación de causas o una causa parcial.")
    return False


def probar(nombre: str, condicion: bool, mensaje: str = "") -> bool:
    """Ejecuta una verificación tipo assert y muestra el resultado sin detener el cuaderno."""
    try:
        assert condicion, mensaje
        print(f"✅ {nombre}")
        return True
    except AssertionError as e:
        print(f"❌ {nombre}: {e}")
        return False
