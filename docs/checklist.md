# Checklist · Cuando los números no cuadran

## Antes de empezar
- [ ] Tengo **las dos cifras** y **el SQL o la lógica real** de cada reporte (no la descripción).
- [ ] Puedo **reproducir** ambas cifras. Si no, ahí está el primer problema.

## Los 7 pasos
1. **Confirmar y acotar**
   - [ ] ¿La diferencia está en todo el periodo o en ciertos días, canales, sucursales o clientes?
   - [ ] Compara por día. Suma las diferencias **absolutas**: si es mucho mayor que la neta, hay causas que se tapan.
   - [ ] Una diferencia que se compensa entre días es de **fecha**; la que no se compensa es de **monto**.
2. **Comparar definiciones**
   - [ ] ¿Bruto o neto? ¿Con o sin IVA? ¿Qué estatus cuenta?
   - [ ] ¿Qué fecha (pedido, pago, entrega, registro)? ¿En qué **zona horaria**?
   - [ ] ¿Qué corte de datos usó cada reporte?
3. **Mismo grano, y contar filas**
   - [ ] ¿Qué representa un renglón en cada tabla?
   - [ ] Cuenta filas **antes y después de cada JOIN**. Si cambia, cambió el grano.
   - [ ] Compara **registro contra registro** (`FULL OUTER JOIN` por llave) antes de comparar totales.
4. **Partir en dos** (fecha, canal, fuente, segmento) hasta que la diferencia quede en un solo lado.
5. **Aislar** los registros responsables. Pocos registros, muy concretos.
6. **Explicar y demostrar** con una consulta que cualquiera pueda volver a ejecutar.
7. **Volverlo prueba** (`assert` / `pytest`) para que no regrese.

## Causas que más se repiten
| Causa | Señal | Consulta típica |
|---|---|---|
| JOIN que multiplica filas | el conteo sube tras un JOIN | `GROUP BY llave HAVING COUNT(*) > 1` |
| JOIN que pierde filas | el conteo baja tras un `INNER JOIN` | `LEFT JOIN ... WHERE derecha IS NULL` |
| Zona horaria | ventas a horas imposibles; diferencias el primer y último día | distribución por hora; columna con zona explícita |
| Definición | dos cifras correctas que miden cosas distintas | leer el SQL; tabla de definiciones |
| Datos tardíos | el reporte “en vivo” tiene más que el del cierre | `recibido_en > corte` |
| Unidades | factor de 100, 1.16, 1000 | promedios y mínimos por columna |
| Nombre engañoso | `total` que no es total | comparar la columna con su cálculo |
| Redondeo | diferencias de centavos en muchos registros | sumar y fijar una tolerancia |

## El puente de conciliación
- [ ] Cada causa con su monto y su **signo** sobre (A − B).
- [ ] **Residuo 0**. Si no, falta una causa.
- [ ] Residuo 0 **no** basta: cada línea necesita su consulta de evidencia.

## Para cada causa decide
- **Arreglar**: es un error (bug). Se corrige y se agrega una prueba.
- **Documentar**: es correcto pero confuso (nombres, unidades, tolerancias).
- **Decidir con negocio**: las dos cifras son válidas y alguien con autoridad elige (definiciones, cortes, reaperturas).
