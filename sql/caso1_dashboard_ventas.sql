-- Dashboard de ventas (equipo comercial)
-- Autor: equipo de BI · Última modificación: julio 2026
-- "Ventas del mes: solo pedidos pagados"
SELECT
    CAST(p.fecha_pedido AS DATE)              AS dia,
    SUM(l.cantidad * l.precio_unitario)       AS ventas
FROM pedidos p
JOIN lineas_pedido l ON l.pedido_id = p.pedido_id
JOIN pagos g         ON g.pedido_id = p.pedido_id   -- para quedarnos solo con pedidos pagados
WHERE CAST(p.fecha_pedido AS DATE) BETWEEN DATE '{desde}' AND DATE '{hasta}'
GROUP BY 1
ORDER BY 1;
