-- Reporte de ingresos (equipo de finanzas)
-- Ingreso neto = pagos recibidos en el mes - devoluciones registradas en el mes.
-- Fechas en hora de Mérida (cierre contable local).
WITH ingresos AS (
    SELECT CAST(pagado_en AT TIME ZONE 'America/Merida' AS DATE) AS dia, SUM(monto) AS monto
    FROM pagos
    GROUP BY 1
),
devs AS (
    SELECT fecha_devolucion AS dia, SUM(monto) AS monto
    FROM devoluciones
    GROUP BY 1
)
SELECT
    i.dia,
    i.monto - COALESCE(d.monto, 0) AS ingreso_neto
FROM ingresos i
LEFT JOIN devs d USING (dia)
WHERE i.dia BETWEEN DATE '{desde}' AND DATE '{hasta}'
ORDER BY 1;
