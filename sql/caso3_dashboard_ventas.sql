-- Dashboard de ventas por segmento y categoría (equipo comercial)
-- Fuente: almacén de datos (DW), se refresca cada hora.
-- Definición acordada en oct-2026: venta bruta SIN IVA, por fecha local del pedido.
SELECT
    c.segmento,
    pr.categoria,
    SUM(l.cantidad * l.precio_unitario) AS ventas_sin_iva
FROM pedidos p
JOIN lineas_pedido l ON l.pedido_id   = p.pedido_id
JOIN productos pr    ON pr.producto_id = l.producto_id
JOIN clientes c      ON c.cliente_id  = p.cliente_id
WHERE p.fecha_pedido_local >= TIMESTAMP '{desde} 00:00:00'
  AND p.fecha_pedido_local <  TIMESTAMP '{hasta} 00:00:00' + INTERVAL 1 DAY
GROUP BY 1, 2
ORDER BY 1, 2;
