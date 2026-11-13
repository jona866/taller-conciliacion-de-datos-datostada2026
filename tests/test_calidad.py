"""
Pruebas automáticas que nacen de los hallazgos del taller.
Cada prueba corresponde a una causa que ya nos costó una tarde de investigación.

Ejecutar:   NNC_DATOS=caso3 python -m pytest -q tests
            NNC_DATOS=carga_nueva python -m pytest -q tests
"""
from decimal import Decimal

import pytest

import nnc

TOLERANCIA = Decimal("10.00")  # pesos; cubre redondeos de IVA por ticket (acordado con finanzas)


def escalar(con, sql):
    return con.execute(sql).fetchone()[0]


def test_join_del_dashboard_no_multiplica_filas(con, params):
    """Unir con productos y clientes no debe cambiar el número de líneas (hallazgos: caso 1 y caso 3)."""
    filtro = f"p.fecha_pedido_local >= TIMESTAMP '{params['desde']} 00:00:00' AND p.fecha_pedido_local < TIMESTAMP '{params['hasta']} 00:00:00' + INTERVAL 1 DAY"
    antes = escalar(con, f"SELECT COUNT(*) FROM pedidos p JOIN lineas_pedido l USING (pedido_id) WHERE {filtro}")
    despues = escalar(con, f"""SELECT COUNT(*) FROM pedidos p
                               JOIN lineas_pedido l ON l.pedido_id = p.pedido_id
                               JOIN productos pr ON pr.producto_id = l.producto_id
                               JOIN clientes c ON c.cliente_id = p.cliente_id
                               WHERE {filtro}""")
    assert antes == despues, f"El join cambia el conteo de líneas: {antes} antes, {despues} después"


@pytest.mark.parametrize("tabla,llave", [("pedidos", "pedido_id"), ("clientes", "cliente_id"),
                                         ("productos", "producto_id")])
def test_llave_unica(con, tabla, llave):
    repetidas = con.execute(f"SELECT {llave}, COUNT(*) n FROM {tabla} GROUP BY 1 HAVING n > 1").fetchall()
    assert not repetidas, f"{tabla}.{llave} tiene valores repetidos: {repetidas[:5]}"


def test_sin_productos_inexistentes(con):
    huerfanas = escalar(con, """SELECT COUNT(*) FROM lineas_pedido l
                                LEFT JOIN productos pr ON pr.producto_id = l.producto_id
                                WHERE pr.producto_id IS NULL""")
    assert huerfanas == 0, f"{huerfanas} líneas apuntan a productos que no existen en el catálogo"


def test_cargas_llegaron_antes_del_corte(con, params):
    tarde = con.execute(f"""SELECT sucursal, MIN(recibido_en) AS recibido, COUNT(*) AS tickets
                        FROM caja_sucursal
                        WHERE CAST(fecha_hora AS DATE) BETWEEN DATE '{params['desde']}' AND DATE '{params['hasta']}'
                          AND recibido_en > TIMESTAMP '{params['corte']}'
                        GROUP BY 1""").fetchall()
    assert not tarde, f"Cargas recibidas después del corte {params['corte']}: {tarde}"


def test_diferencia_entre_reportes_dentro_de_tolerancia(con, caso):
    comercial = nnc.total(con, "caso3_dashboard_ventas", caso)
    finanzas = nnc.total(con, "caso3_reporte_finanzas", caso)
    dif = comercial - finanzas
    assert abs(dif) <= TOLERANCIA, f"Comercial {comercial:,.2f} vs finanzas {finanzas:,.2f}: diferencia {dif:,.2f}"
