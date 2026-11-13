-- Reporte de ventas para el cierre (equipo de finanzas)
-- Fuentes operativas: pasarela de pagos (en línea) y cortes de caja (sucursales).
-- Definición acordada en oct-2026: venta bruta SIN IVA, por fecha local.
-- Corte: se toma lo recibido hasta {corte} (hora de Mérida).
WITH en_linea AS (
    SELECT 'en_linea' AS origen,
           SUM(ROUND(monto / 100.0 / 1.16, 2)) AS ventas_sin_iva   -- la pasarela reporta centavos con IVA
    FROM pasarela_cobros
    WHERE estado = 'aprobado'
      AND CAST(cobrado_en AT TIME ZONE 'America/Merida' AS DATE) BETWEEN DATE '{desde}' AND DATE '{hasta}'
),
sucursales AS (
    SELECT 'sucursales' AS origen,
           SUM(ROUND(importe / 1.16, 2)) AS ventas_sin_iva           -- el ticket trae IVA incluido
    FROM caja_sucursal
    WHERE CAST(fecha_hora AS DATE) BETWEEN DATE '{desde}' AND DATE '{hasta}'
      AND recibido_en <= TIMESTAMP '{corte}'
)
SELECT * FROM en_linea
UNION ALL
SELECT * FROM sucursales;
