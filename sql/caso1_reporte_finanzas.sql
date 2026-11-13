-- Reporte de ingresos (equipo de finanzas)
-- Fuente: tabla de pagos. Fecha: día del pago en hora de Mérida.
SELECT
    CAST(g.pagado_en AT TIME ZONE 'America/Merida' AS DATE) AS dia,
    SUM(g.monto)                                            AS ingresos
FROM pagos g
WHERE CAST(g.pagado_en AT TIME ZONE 'America/Merida' AS DATE) BETWEEN DATE '{desde}' AND DATE '{hasta}'
GROUP BY 1
ORDER BY 1;
