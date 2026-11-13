-- Dashboard de ventas (equipo comercial)
-- Versión corregida en septiembre 2026 después del problema de pagos parciales:
-- ya no se une con pagos; se usa EXISTS para quedarnos con pedidos pagados.
SELECT
    CAST(p.fecha_pedido AS DATE)              AS dia,
    SUM(l.cantidad * l.precio_unitario)       AS ventas
FROM pedidos p
JOIN lineas_pedido l ON l.pedido_id = p.pedido_id
WHERE EXISTS (SELECT 1 FROM pagos g WHERE g.pedido_id = p.pedido_id)
  AND CAST(p.fecha_pedido AS DATE) BETWEEN DATE '{desde}' AND DATE '{hasta}'
GROUP BY 1
ORDER BY 1;
