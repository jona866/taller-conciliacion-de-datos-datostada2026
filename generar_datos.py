"""
Genera los datos ficticios del taller "Los números no cuadran".

Negocio ficticio: Telar & Barro, tienda de artesanías yucatecas con venta
en línea y tres sucursales (Mérida Centro, Valladolid y Progreso).
Todos los nombres de personas y negocios son inventados.

El script es determinista (semilla fija): siempre produce los mismos archivos.
Uso:  python generar_datos.py
"""
from __future__ import annotations

import csv
import hashlib
import json
import random
from datetime import datetime, timedelta, date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
DATOS = RAIZ / "datos"
OFFSET_MERIDA = timedelta(hours=6)  # Mérida = UTC-6 todo el año

# --------------------------------------------------------------------------
# Catálogos
# --------------------------------------------------------------------------
# (sku, nombre, categoria, precio al público CON IVA en pesos enteros)
PRODUCTOS = [
    ("HAM-MAT-ALG", "Hamaca matrimonial de algodón", "Hamacas", 1450),
    ("HAM-IND-ALG", "Hamaca individual de algodón", "Hamacas", 890),
    ("HAM-KS-NYL", "Hamaca king size de nylon", "Hamacas", 1980),
    ("HAM-MEDIDA", "Hamaca a la medida (sobre pedido)", "Hamacas", 3600),
    ("GUA-LIN-ML", "Guayabera de lino manga larga", "Ropa", 1290),
    ("GUA-ALG-MC", "Guayabera de algodón manga corta", "Ropa", 690),
    ("HUI-BORD", "Huipil bordado a mano", "Ropa", 1850),
    ("TER-GALA", "Terno de gala (3 piezas)", "Ropa", 6900),
    ("REB-ALG", "Rebozo de algodón teñido", "Ropa", 760),
    ("SOM-JIPI", "Sombrero de jipi", "Accesorios", 1150),
    ("BOL-HEN", "Bolsa de henequén", "Accesorios", 385),
    ("HUA-PIEL", "Huaraches de piel", "Accesorios", 870),
    ("FIL-ARE", "Aretes de filigrana de plata", "Joyería", 980),
    ("FIL-ROS", "Rosario de filigrana", "Joyería", 1640),
    ("TAP-HEN", "Tapete de henequén 60x90", "Casa", 520),
    ("MAN-BORD", "Mantel bordado 6 puestos", "Casa", 1380),
    ("CER-MAC", "Maceta de barro de Ticul", "Casa", 275),
    ("CER-PLA", "Plato decorativo de Ticul", "Casa", 340),
    ("TAB-CIR", "Tabla de madera de ciricote", "Casa", 450),
    ("VEL-CERA", "Vela de cera de abeja", "Casa", 145),
    ("MIE-250", "Miel melipona 250 ml", "Alimentos", 320),
    ("MIE-500", "Miel melipona 500 ml", "Alimentos", 590),
    ("JAB-MIEL", "Jabón artesanal de miel", "Alimentos", 95),
    ("DUL-COCO", "Dulce de coco (caja)", "Alimentos", 120),
    ("REC-ROJO", "Recado rojo artesanal 500 g", "Alimentos", 110),
    ("XTA-750", "Licor de xtabentún 750 ml", "Alimentos", 410),
]
NOMBRES = ["María", "José", "Guadalupe", "Juan", "Ana", "Luis", "Fernanda", "Carlos",
           "Mariana", "Jorge", "Daniela", "Ricardo", "Sofía", "Miguel", "Valeria",
           "Alejandro", "Andrea", "Raúl", "Gabriela", "Pedro", "Itzel", "Manuel",
           "Citlali", "Roberto", "Paola", "Emilio", "Lucía", "Armando"]
APELLIDOS = ["Pech", "Canché", "Chan", "May", "Puc", "Uc", "Cauich", "Dzul", "Ek", "Poot",
             "Tun", "Hernández", "García", "López", "Martínez", "Pérez", "Rodríguez",
             "Sánchez", "Ramírez", "Cervera", "Peón", "Cámara", "Medina", "Novelo"]
CIUDADES = (["Mérida"] * 8 + ["Valladolid", "Progreso", "Cancún", "Campeche",
            "Ciudad de México", "Monterrey", "Guadalajara", "Puebla", "Querétaro"])
MAYORISTAS = ["Hotel Patio de los Almendros", "Boutique Casa Henequén",
              "Hotel Jardín Poniente", "Tienda Kankab del Aeropuerto",
              "Galería Sac-Bé", "Hostal La Pochota", "Hotel Arcos del Sur",
              "Regalos Uxmalito"]
SUCURSALES = {"MER": "Mérida Centro", "VAL": "Valladolid", "PRO": "Progreso"}


def centavos_sin_iva(precio_con_iva: int) -> int:
    """Precio sin IVA en centavos, redondeado como lo hace el punto de venta."""
    return round(precio_con_iva * 100 / 1.16)


def pesos(c: int) -> str:
    signo = "-" if c < 0 else ""
    c = abs(c)
    return f"{signo}{c // 100}.{c % 100:02d}"


def sha(v) -> str:
    return hashlib.sha256(str(v).encode()).hexdigest()[:16]


# --------------------------------------------------------------------------
# Generador base
# --------------------------------------------------------------------------
class Tienda:
    def __init__(self, semilla: int, n_clientes: int = 260):
        self.rng = random.Random(semilla)
        self.productos = []
        for i, (sku, nom, cat, p) in enumerate(PRODUCTOS, start=1):
            self.productos.append(dict(producto_id=100 + i, sku=sku, nombre=nom,
                                       categoria=cat, precio_con_iva=p,
                                       precio_sin_iva_c=centavos_sin_iva(p)))
        self.clientes = []
        r = self.rng
        for i in range(1, n_clientes + 1):
            nombre = f"{r.choice(NOMBRES)} {r.choice(APELLIDOS)} {r.choice(APELLIDOS)}"
            self.clientes.append(dict(cliente_id=f"C{i:04d}", nombre=nombre,
                                      segmento="minorista", ciudad=r.choice(CIUDADES),
                                      alta=date(2023, 1, 1) + timedelta(days=r.randint(0, 1200))))
        for j, nom in enumerate(MAYORISTAS, start=n_clientes + 1):
            self.clientes.append(dict(cliente_id=f"C{j:04d}", nombre=nom, segmento="mayorista",
                                      ciudad=r.choice(["Mérida", "Mérida", "Cancún", "Valladolid"]),
                                      alta=date(2022, 6, 1) + timedelta(days=r.randint(0, 900))))
        self.minoristas = [c for c in self.clientes if c["segmento"] == "minorista"]
        self.mayoristas = [c for c in self.clientes if c["segmento"] == "mayorista"]
        self.seq = {"WEB": 48000, "MER": 12000, "VAL": 5000, "PRO": 3000}
        self.linea_seq = 0

    def prod(self, sku):
        return next(p for p in self.productos if p["sku"] == sku)

    def nuevo_id(self, origen):
        self.seq[origen] += self.rng.randint(1, 3)  # huecos, como en la vida real
        return f"{origen}-{self.seq[origen]:06d}"

    def lineas(self, pedido_id, mayorista=False, forzar_sku=None, excluir=()):
        r = self.rng
        out = []
        if forzar_sku:
            elegidos = [self.prod(forzar_sku)]
        else:
            cand = [p for p in self.productos if p["sku"] not in excluir and p["sku"] != "HAM-MEDIDA"]
            n = r.choice([1, 1, 1, 2, 2, 3, 4])
            elegidos = r.sample(cand, n)
        for p in elegidos:
            if mayorista:
                cant = r.randint(6, 20)
            else:
                cant = r.choice([1, 1, 1, 1, 2, 2, 3])
            self.linea_seq += 1
            out.append(dict(linea_id=self.linea_seq, pedido_id=pedido_id, producto_id=p["producto_id"],
                            cantidad=cant, precio_c=p["precio_sin_iva_c"]))
        return out

    def hora_local(self, dia: date, canal: str, desde=None, hasta=None):
        r = self.rng
        if canal == "en_linea":
            # compras en línea: todo el día, más por la noche
            h = r.choices(range(24), weights=[2, 1, 1, 1, 1, 1, 2, 3, 4, 5, 6, 6, 6, 6, 6, 6, 6, 7, 8, 9, 10, 10, 8, 5])[0]
        else:
            h = r.randint(9, 19)  # horario de sucursal
        if desde is not None:
            h = max(h, desde)
        if hasta is not None:
            h = min(h, hasta)
        return datetime(dia.year, dia.month, dia.day, h, r.randint(0, 59), r.randint(0, 59))


def subtotal_c(lineas):
    return sum(l["cantidad"] * l["precio_c"] for l in lineas)


def escribir_csv(carpeta: Path, nombre: str, filas: list[dict], columnas: list[str]):
    carpeta.mkdir(parents=True, exist_ok=True)
    with open(carpeta / f"{nombre}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=columnas, lineterminator="\n")
        w.writeheader()
        for fila in filas:
            w.writerow({k: fila[k] for k in columnas})


def dias(desde: date, hasta: date):
    d = desde
    while d <= hasta:
        yield d
        d += timedelta(days=1)


def fmt_local(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def fmt_utc_naive(dt_local):
    return (dt_local + OFFSET_MERIDA).strftime("%Y-%m-%d %H:%M:%S")


def iso_z(dt_local):
    return (dt_local + OFFSET_MERIDA).strftime("%Y-%m-%dT%H:%M:%SZ")


def iso_local(dt_local):
    return dt_local.strftime("%Y-%m-%dT%H:%M:%S-06:00")


def filas_productos(t: Tienda, quitar=()):
    return [dict(producto_id=p["producto_id"], sku=p["sku"], nombre=p["nombre"], categoria=p["categoria"],
                 precio_lista=pesos(p["precio_sin_iva_c"]))
            for p in t.productos if p["sku"] not in quitar]


def filas_clientes(t: Tienda):
    return [dict(cliente_id=c["cliente_id"], nombre=c["nombre"], segmento=c["segmento"],
                 ciudad=c["ciudad"], fecha_alta=c["alta"].isoformat()) for c in t.clientes]


# --------------------------------------------------------------------------
# Esquema operativo (casos 1 y 2)
# --------------------------------------------------------------------------
def generar_operativo(t: Tienda, desde: date, hasta: date, por_dia_web: int, por_dia_suc: int,
                      hora_max_ultimo_dia_web=None):
    """Pedidos tal como los guarda el sistema: en línea en hora del servidor (UTC, sin zona),
    sucursal en hora local (sin zona). Pagos con desplazamiento explícito."""
    r = t.rng
    pedidos, lineas, pagos = [], [], []
    for d in dias(desde, hasta):
        n_web = max(1, int(r.gauss(por_dia_web, por_dia_web * 0.25)))
        n_suc = max(1, int(r.gauss(por_dia_suc, por_dia_suc * 0.25)))
        for _ in range(n_web):
            hasta_h = hora_max_ultimo_dia_web if (d == hasta and hora_max_ultimo_dia_web is not None) else None
            loc = t.hora_local(d, "en_linea", hasta=hasta_h)
            agregar_pedido(t, pedidos, lineas, pagos, "en_linea", loc)
        for _ in range(n_suc):
            loc = t.hora_local(d, "sucursal")
            agregar_pedido(t, pedidos, lineas, pagos, "sucursal", loc)
    return pedidos, lineas, pagos


def agregar_pedido(t, pedidos, lineas, pagos, canal, loc, cliente=None, forzar_sku=None,
                   pagos_parciales=None, estatus="pagado", origen=None):
    r = t.rng
    if cliente is None:
        cliente = r.choice(t.mayoristas) if r.random() < 0.03 else r.choice(t.minoristas)
    if canal == "en_linea":
        origen = "WEB"
    elif origen is None:
        origen = r.choices(["MER", "VAL", "PRO"], weights=[6, 2, 2])[0]
    pid = t.nuevo_id(origen)
    ls = t.lineas(pid, mayorista=cliente["segmento"] == "mayorista", forzar_sku=forzar_sku)
    total = subtotal_c(ls)
    p = dict(pedido_id=pid, cliente_id=cliente["cliente_id"], canal=canal,
             sucursal="" if canal == "en_linea" else SUCURSALES[origen],
             fecha_pedido=fmt_utc_naive(loc) if canal == "en_linea" else fmt_local(loc),
             estatus=estatus, _loc=loc, _total=total)
    pedidos.append(p)
    lineas.extend(ls)
    if estatus != "pagado":
        return p
    # pagos
    partes = pagos_parciales or [(1.0, timedelta(seconds=r.randint(5, 90)))]
    acumulado = 0
    for i, (frac, desfase) in enumerate(partes):
        monto = total - acumulado if i == len(partes) - 1 else round(total * frac)
        acumulado += monto
        cuando = loc + desfase
        pagos.append(dict(pago_id=f"PG{len(pagos) + 1:06d}", pedido_id=pid,
                          metodo=("tarjeta" if canal == "en_linea" else r.choice(["efectivo", "tarjeta", "transferencia"])),
                          monto=pesos(monto),
                          pagado_en=iso_z(cuando) if canal == "en_linea" else iso_local(cuando),
                          _loc=cuando, _c=monto))
    return p


COLS_PEDIDOS = ["pedido_id", "cliente_id", "canal", "sucursal", "fecha_pedido", "estatus"]
COLS_LINEAS = ["linea_id", "pedido_id", "producto_id", "cantidad", "precio_unitario"]
COLS_PAGOS = ["pago_id", "pedido_id", "metodo", "monto", "pagado_en"]
COLS_PRODUCTOS = ["producto_id", "sku", "nombre", "categoria", "precio_lista"]
COLS_CLIENTES = ["cliente_id", "nombre", "segmento", "ciudad", "fecha_alta"]


def lineas_out(ls):
    return [dict(l, precio_unitario=pesos(l["precio_c"])) for l in ls]


# --------------------------------------------------------------------------
# Caso 1: agosto 2026. Un join que multiplica filas.
# --------------------------------------------------------------------------
def caso1(respuestas):
    t = Tienda(semilla=2608)
    r = t.rng
    pedidos, lineas, pagos = generar_operativo(t, date(2026, 8, 1), date(2026, 8, 31), 11, 7,
                                               hora_max_ultimo_dia_web=17)
    # Apartados: hamacas a la medida y pedidos de mayoreo pagados en partes (todo dentro de agosto)
    apartados = []
    for i in range(11):
        d = date(2026, 8, r.randint(1, 18))
        loc = t.hora_local(d, "sucursal")
        p = agregar_pedido(t, pedidos, lineas, pagos, "sucursal", loc, cliente=r.choice(t.minoristas),
                           forzar_sku="HAM-MEDIDA", origen="MER",
                           pagos_parciales=[(0.5, timedelta(minutes=3)),
                                            (0.5, timedelta(days=r.randint(4, 11), hours=r.randint(0, 3)))])
        apartados.append(p)
    # un mayorista que pagó en tres exhibiciones
    loc = t.hora_local(date(2026, 8, 6), "sucursal")
    p = agregar_pedido(t, pedidos, lineas, pagos, "sucursal", loc, cliente=t.mayoristas[0], origen="MER",
                       pagos_parciales=[(0.3, timedelta(minutes=5)), (0.3, timedelta(days=7)),
                                        (0.4, timedelta(days=16))])
    apartados.append(p)
    # Pedidos en línea abandonados (sin pago): ambos reportes los excluyen a propósito
    for _ in range(14):
        d = date(2026, 8, r.randint(1, 30))
        agregar_pedido(t, pedidos, lineas, pagos, "en_linea", t.hora_local(d, "en_linea"), estatus="pendiente")

    carpeta = DATOS / "caso1"
    escribir_csv(carpeta, "pedidos", pedidos, COLS_PEDIDOS)
    escribir_csv(carpeta, "lineas_pedido", lineas_out(lineas), COLS_LINEAS)
    escribir_csv(carpeta, "pagos", pagos, COLS_PAGOS)
    escribir_csv(carpeta, "productos", filas_productos(t), COLS_PRODUCTOS)
    escribir_csv(carpeta, "clientes", filas_clientes(t), COLS_CLIENTES)

    # respuestas esperadas
    n_pagos = {}
    for g in pagos:
        n_pagos[g["pedido_id"]] = n_pagos.get(g["pedido_id"], 0) + 1
    tot = {p["pedido_id"]: p["_total"] for p in pedidos}
    pagados = [p for p in pedidos if p["estatus"] == "pagado"]
    real = sum(p["_total"] for p in pagados)
    dashboard = sum(tot[pid] * n for pid, n in n_pagos.items())
    finanzas = sum(g["_c"] for g in pagos)
    assert finanzas == real
    multi = sorted(pid for pid, n in n_pagos.items() if n > 1)
    lineas_por = {}
    for l in lineas:
        lineas_por[l["pedido_id"]] = lineas_por.get(l["pedido_id"], 0) + 1
    filas_antes = sum(lineas_por[p["pedido_id"]] for p in pagados)
    filas_despues = sum(lineas_por[pid] * n for pid, n in n_pagos.items())
    respuestas["caso1"] = dict(dashboard=pesos(dashboard), finanzas=pesos(finanzas),
                               diferencia=pesos(dashboard - finanzas), pedidos_multipago=len(multi),
                               filas_antes=filas_antes, filas_despues=filas_despues,
                               pedidos_sin_pago=sum(1 for p in pedidos if p["estatus"] != "pagado"))
    return respuestas["caso1"]


# --------------------------------------------------------------------------
# Caso 2: octubre 2026. Zona horaria + definición (bruto vs neto) que se tapan.
# --------------------------------------------------------------------------
def caso2(respuestas, objetivo=(1500_00, 4500_00)):
    t = Tienda(semilla=2610)
    r = t.rng
    pedidos, lineas, pagos = generar_operativo(t, date(2026, 9, 29), date(2026, 11, 1), 22, 12)
    # Campaña Hanal Pixán: envío gratis hasta el 31 de octubre a las 23:59 (hora de Mérida)
    campana = []
    for _ in range(400):
        loc = datetime(2026, 10, 31, r.randint(18, 23), r.randint(0, 59), r.randint(0, 59))
        campana.append(loc)
    # Devoluciones registradas en octubre (algunas de pedidos de septiembre)
    candidatos = [p for p in pedidos if p["estatus"] == "pagado" and date(2026, 9, 20) <= p["_loc"].date() <= date(2026, 10, 25)]
    devoluciones = []
    lin_por = {}
    for l in lineas:
        lin_por.setdefault(l["pedido_id"], []).append(l)
    for i, p in enumerate(r.sample(candidatos, 75)):
        l = r.choice(lin_por[p["pedido_id"]])
        monto = l["precio_c"] * (1 if l["cantidad"] == 1 else r.randint(1, l["cantidad"]))
        f = p["_loc"].date() + timedelta(days=r.randint(2, 12))
        f = min(max(f, date(2026, 10, 1)), date(2026, 10, 31))
        devoluciones.append(dict(devolucion_id=f"DV{i + 1:04d}", pedido_id=p["pedido_id"],
                                 fecha_devolucion=f.isoformat(),
                                 motivo=r.choice(["talla incorrecta", "defecto de fábrica", "llegó dañado",
                                                  "no le gustó", "color distinto"]),
                                 monto=pesos(monto), _c=monto))

    def reportes(pedidos, pagos):
        oct1, oct31 = date(2026, 10, 1), date(2026, 10, 31)
        dash = sum(p["_total"] for p in pedidos if p["estatus"] == "pagado"
                   and oct1 <= datetime.strptime(p["fecha_pedido"], "%Y-%m-%d %H:%M:%S").date() <= oct31)
        ingresos = sum(g["_c"] for g in pagos if oct1 <= g["_loc"].date() <= oct31)
        dev = sum(d["_c"] for d in devoluciones)
        return dash, ingresos, dev

    # agrega pedidos de campaña uno por uno hasta que la diferencia neta quede pequeña
    campana.sort()
    usados = 0
    while True:
        dash, ing, dev = reportes(pedidos, pagos)
        diff = dash - (ing - dev)
        if diff <= objetivo[1]:
            break
        agregar_pedido(t, pedidos, lineas, pagos, "en_linea", campana[usados], cliente=r.choice(t.minoristas))
        usados += 1
    assert objetivo[0] <= diff <= objetivo[1], diff

    carpeta = DATOS / "caso2"
    escribir_csv(carpeta, "pedidos", pedidos, COLS_PEDIDOS)
    escribir_csv(carpeta, "lineas_pedido", lineas_out(lineas), COLS_LINEAS)
    escribir_csv(carpeta, "pagos", pagos, COLS_PAGOS)
    escribir_csv(carpeta, "devoluciones", devoluciones, ["devolucion_id", "pedido_id", "fecha_devolucion", "motivo", "monto"])
    escribir_csv(carpeta, "productos", filas_productos(t), COLS_PRODUCTOS)
    escribir_csv(carpeta, "clientes", filas_clientes(t), COLS_CLIENTES)

    oct1, oct31 = date(2026, 10, 1), date(2026, 10, 31)
    web = [p for p in pedidos if p["canal"] == "en_linea"]
    entran = sum(p["_total"] for p in web if p["_loc"].date() < oct1 and
                 oct1 <= datetime.strptime(p["fecha_pedido"], "%Y-%m-%d %H:%M:%S").date())
    salen = sum(p["_total"] for p in web if oct1 <= p["_loc"].date() <= oct31 and
                datetime.strptime(p["fecha_pedido"], "%Y-%m-%d %H:%M:%S").date() > oct31)
    efecto_tz = entran - salen
    assert diff == efecto_tz + dev
    respuestas["caso2"] = dict(dashboard=pesos(dash), finanzas=pesos(ing - dev), diferencia=pesos(diff),
                               efecto_zona_horaria=pesos(efecto_tz), efecto_devoluciones=pesos(dev),
                               pedidos_campana=usados, entran_de_septiembre=pesos(entran),
                               salen_a_noviembre=pesos(salen))
    return respuestas["caso2"]


# --------------------------------------------------------------------------
# Caso 3: octubre 2026, almacén de datos (DW) vs fuentes operativas.
# --------------------------------------------------------------------------
CORTE_C3 = datetime(2026, 11, 3, 9, 0, 0)


def generar_dw(t: Tienda, desde: date, hasta: date, por_dia_web, por_dia_suc, corte: datetime,
               tardia: tuple | None, cliente_dup_idx: int | None, skus_huerfanos=(), sku_duplicado=None):
    """Devuelve tablas del DW y de las fuentes operativas, más los efectos sembrados (en centavos)."""
    r = t.rng
    pedidos, lineas, cobros, tickets, cargas = [], [], [], [], []
    efectos = dict(cliente_duplicado=0, producto_huerfano=0, carga_tardia=0, producto_duplicado=0)
    dup_cliente = t.mayoristas[cliente_dup_idx] if cliente_dup_idx is not None else None
    huerfanos = {t.prod(s)["producto_id"] for s in skus_huerfanos}
    dup_prod = t.prod(sku_duplicado)["producto_id"] if sku_duplicado else None
    cobro_seq = 700000
    precio_con_iva = {p["producto_id"]: p["precio_con_iva"] for p in t.productos}
    # cargas diarias: cada sucursal sube su corte de caja al día siguiente a las 02:00
    for d in dias(desde, hasta):
        n_web = max(1, int(r.gauss(por_dia_web, por_dia_web * 0.25)))
        n_suc = max(1, int(r.gauss(por_dia_suc, por_dia_suc * 0.25)))
        canales = ["en_linea"] * n_web + ["sucursal"] * n_suc
        # el cliente duplicado compra algunos días
        for canal in canales:
            es_dup = dup_cliente is not None and canal == "sucursal" and r.random() < 0.02
            cliente = dup_cliente if es_dup else (r.choice(t.mayoristas[1:]) if r.random() < 0.03 else r.choice(t.minoristas))
            origen = "WEB" if canal == "en_linea" else ("MER" if es_dup else r.choices(["MER", "VAL", "PRO"], weights=[6, 2, 2])[0])
            loc = t.hora_local(d, canal)
            if loc.hour == 23 and loc.minute >= 58:
                loc = loc.replace(minute=50)
            pid = t.nuevo_id(origen)
            excluir = () if not (es_dup or origen == "VAL") else tuple(skus_huerfanos)
            ls = t.lineas(pid, mayorista=cliente["segmento"] == "mayorista", excluir=excluir)
            tot = subtotal_c(ls)
            recibido = datetime(d.year, d.month, d.day, 2, 0) + timedelta(days=1)
            if canal == "sucursal" and tardia and origen == tardia[0] and d >= tardia[1]:
                recibido = tardia[2]
            elif canal == "en_linea":
                recibido = loc + timedelta(minutes=r.randint(5, 40))
            pedidos.append(dict(pedido_id=pid, cliente_id=cliente["cliente_id"], canal=canal,
                                sucursal="" if canal == "en_linea" else SUCURSALES[origen],
                                fecha_pedido_local=fmt_local(loc), total=pesos(tot),
                                cargado_en=fmt_local(recibido + timedelta(minutes=30)), _tot=tot, _rec=recibido))
            lineas.extend(ls)
            # el cliente paga el precio de lista CON IVA; el DW guarda precio unitario SIN IVA redondeado
            con_iva = sum(l["cantidad"] * precio_con_iva[l["producto_id"]] * 100 for l in ls)
            if canal == "en_linea":
                if r.random() < 0.06:  # intento rechazado antes del cobro bueno
                    cobro_seq += r.randint(1, 4)
                    cobros.append(dict(cobro_id=f"ch_{cobro_seq}", referencia=pid, monto=con_iva, moneda="MXN",
                                       estado="rechazado", cobrado_en=iso_z(loc + timedelta(seconds=20))))
                cobro_seq += r.randint(1, 4)
                cobros.append(dict(cobro_id=f"ch_{cobro_seq}", referencia=pid, monto=con_iva, moneda="MXN",
                                   estado="aprobado", cobrado_en=iso_z(loc + timedelta(seconds=r.randint(30, 80)))))
            else:
                tickets.append(dict(ticket_id=f"T{origen}{len(tickets) + 1:06d}", pedido_id=pid,
                                    sucursal=SUCURSALES[origen], importe=pesos(con_iva),
                                    fecha_hora=fmt_local(loc), recibido_en=fmt_local(recibido)))
            # efectos sembrados
            if es_dup:
                efectos["cliente_duplicado"] += tot
            if canal == "sucursal" and recibido > corte:
                efectos["carga_tardia"] += tot
            for l in ls:
                if l["producto_id"] in huerfanos:
                    efectos["producto_huerfano"] += l["cantidad"] * l["precio_c"]
                if l["producto_id"] == dup_prod:
                    efectos["producto_duplicado"] += l["cantidad"] * l["precio_c"]
    # bitácora de cargas
    por_carga = {}
    for tk in tickets:
        k = (tk["sucursal"], tk["recibido_en"])
        por_carga[k] = por_carga.get(k, 0) + 1
    for i, ((suc, rec), n) in enumerate(sorted(por_carga.items(), key=lambda x: x[0][1]), start=1):
        cargas.append(dict(carga_id=i, fuente="caja_sucursal", sucursal=suc, recibido_en=rec, filas=n))
    return pedidos, lineas, cobros, tickets, cargas, efectos


def caso_dw(nombre, respuestas, semilla, desde, hasta, corte, tardia, cliente_dup_idx, skus_huerfanos,
            sku_duplicado, por_dia_web=26, por_dia_suc=16):
    t = Tienda(semilla=semilla)
    pedidos, lineas, cobros, tickets, cargas, ef = generar_dw(t, desde, hasta, por_dia_web, por_dia_suc,
                                                              corte, tardia, cliente_dup_idx,
                                                              skus_huerfanos, sku_duplicado)
    clientes = filas_clientes(t)
    if cliente_dup_idx is not None:
        # recarga del CRM: el cliente cambió de razón social y se insertó otra vez con el mismo id
        orig = next(c for c in clientes if c["cliente_id"] == t.mayoristas[cliente_dup_idx]["cliente_id"])
        nuevo = dict(orig, nombre=orig["nombre"] + " S.A. de C.V.")
        clientes.insert(clientes.index(orig) + 37, nuevo)
    clientes_out = []
    for c in clientes:
        c2 = dict(c)
        c2["cargado_en"] = "2026-09-01 02:30:00"
        clientes_out.append(c2)
    if cliente_dup_idx is not None:
        clientes_out[[i for i, c in enumerate(clientes_out) if c["nombre"].endswith("S.A. de C.V.")][0]]["cargado_en"] = "2026-10-12 02:30:00"
    productos = filas_productos(t, quitar=skus_huerfanos)
    if sku_duplicado:
        p = next(x for x in productos if x["sku"] == sku_duplicado)
        nuevo = dict(p, nombre=p["nombre"] + " (nuevo empaque)", precio_lista=pesos(round(float(p["precio_lista"]) * 100 * 1.08)))
        productos.append(nuevo)

    carpeta = DATOS / nombre
    escribir_csv(carpeta, "pedidos", pedidos, ["pedido_id", "cliente_id", "canal", "sucursal", "fecha_pedido_local", "total", "cargado_en"])
    escribir_csv(carpeta, "lineas_pedido", lineas_out(lineas), COLS_LINEAS)
    escribir_csv(carpeta, "productos", productos, COLS_PRODUCTOS)
    escribir_csv(carpeta, "clientes", clientes_out, COLS_CLIENTES + ["cargado_en"])
    escribir_csv(carpeta, "pasarela_cobros", cobros, ["cobro_id", "referencia", "monto", "moneda", "estado", "cobrado_en"])
    escribir_csv(carpeta, "caja_sucursal", tickets, ["ticket_id", "pedido_id", "sucursal", "importe", "fecha_hora", "recibido_en"])
    escribir_csv(carpeta, "cargas", cargas, ["carga_id", "fuente", "sucursal", "recibido_en", "filas"])

    # reportes calculados de forma independiente (en centavos)
    base = sum(p["_tot"] for p in pedidos)
    rep_a = base + ef["cliente_duplicado"] - ef["producto_huerfano"] + ef["producto_duplicado"]
    # reporte B: ROUND(con_iva/1.16, 2) por transacción
    rnd = 0
    rep_b = 0
    for c in cobros:
        if c["estado"] == "aprobado":
            v = round(c["monto"] / 1.16)
            rep_b += v
    for tk in tickets:
        if datetime.strptime(tk["recibido_en"], "%Y-%m-%d %H:%M:%S") <= corte:
            c = int(tk["importe"].replace(".", ""))
            rep_b += round(c / 1.16)
    incluido = base - ef["carga_tardia"]
    rnd = rep_b - incluido
    diff = rep_a - rep_b
    assert diff == ef["cliente_duplicado"] - ef["producto_huerfano"] + ef["producto_duplicado"] + ef["carga_tardia"] - rnd
    respuestas[nombre] = dict(reporte_comercial=pesos(rep_a), reporte_finanzas=pesos(rep_b), diferencia=pesos(diff),
                              cliente_duplicado=pesos(ef["cliente_duplicado"]),
                              producto_huerfano=pesos(-ef["producto_huerfano"]),
                              producto_duplicado=pesos(ef["producto_duplicado"]),
                              carga_tardia=pesos(ef["carga_tardia"]), redondeo=pesos(-rnd),
                              corte=corte.strftime("%Y-%m-%d %H:%M:%S"),
                              cliente_dup_id=t.mayoristas[cliente_dup_idx]["cliente_id"] if cliente_dup_idx is not None else None,
                              skus_huerfanos=list(skus_huerfanos))
    return respuestas[nombre]


def main():
    respuestas = {}
    print("caso1", caso1(respuestas))
    print("caso2", caso2(respuestas))
    print("caso3", caso_dw("caso3", respuestas, 3610, date(2026, 10, 1), date(2026, 10, 31), CORTE_C3,
                           tardia=("VAL", date(2026, 10, 28), datetime(2026, 11, 4, 10, 15, 0)),
                           cliente_dup_idx=0, skus_huerfanos=("JAB-MIEL", "DUL-COCO"), sku_duplicado=None))
    print("carga_nueva", caso_dw("carga_nueva", respuestas, 3611, date(2026, 11, 1), date(2026, 11, 8),
                                 datetime(2026, 11, 9, 9, 0, 0), tardia=None, cliente_dup_idx=None,
                                 skus_huerfanos=(), sku_duplicado="MIE-500"))
    # Respuestas para el facilitador (texto claro) y para los cuadernos (hash, sin spoiler)
    (DATOS / "_respuestas_facilitador.json").write_text(json.dumps(respuestas, indent=2, ensure_ascii=False), encoding="utf-8")
    hashes = {}
    for caso, d in respuestas.items():
        for k, v in d.items():
            if isinstance(v, (str, int)):
                hashes[f"{caso}.{k}"] = sha(v)
    # hallazgos del caso 3 sin nombre de causa (para no dar pistas)
    hashes["caso3.hallazgos"] = sorted(sha(respuestas["caso3"][k]) for k in
                                       ("cliente_duplicado", "producto_huerfano", "carga_tardia", "redondeo"))
    hashes["caso3.hallazgos_abs"] = sorted(sha(respuestas["caso3"][k].lstrip("-")) for k in
                                           ("cliente_duplicado", "producto_huerfano", "carga_tardia", "redondeo"))
    (DATOS / "verificacion.json").write_text(json.dumps(hashes, indent=2), encoding="utf-8")
    # manifiesto para check_setup: filas por archivo
    manifiesto = {}
    for f in sorted(DATOS.glob("*/*.csv")):
        with open(f, encoding="utf-8") as fh:
            manifiesto[f"{f.parent.name}/{f.name}"] = sum(1 for _ in fh) - 1
    (DATOS / "manifiesto.json").write_text(json.dumps(manifiesto, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
