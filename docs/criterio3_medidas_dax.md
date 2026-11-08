# Criterio 3 — Catálogo de medidas DAX

**Proyecto:** BI Purchasing — AdventureWorks2  
**Responsable:** Molina  
**Archivos fuente:** `powerbi/medidas_basicas.dax` y `powerbi/medidas_avanzadas.dax`

---

## 1. Cómo agregar las medidas en Power BI

1. En Power BI Desktop, ir a **Inicio → Escribir datos**.
2. Crear una tabla de una sola columna llamada `_Medidas` (por ejemplo, columna `Valor`, con una fila vacía). No se usa para visuales; solo es el contenedor de medidas.
3. Clic derecho en `_Medidas` → **Nueva medida**.
4. Pegar la expresión que aparece después del signo `=` en este catálogo.
5. En **Propiedades → Carpeta de presentación**, asignar `01 Básicas`, `02 Avanzadas` o `03 Órdenes`.
6. En **Herramientas de medida → Formato**, aplicar el formato indicado.

> Las medidas se calculan sobre el modelo, no sobre una tabla en particular. Por eso se guardan en `_Medidas` y no en `FactCompras` o `FactOrdenes`.

---

## 2. Medidas básicas (carpeta `01 Básicas`)

Estas son las que Sebastián necesita para las tarjetas KPI.

| # | Medida | Formato | Qué calcula | Fórmula |
|---:|---|---|---|---|
| 1 | `Total Comprado` | Moneda | Suma el valor de las líneas (`LineTotal`), sin impuestos ni flete. | `SUM ( FactCompras[TotalLinea] )` |
| 2 | `Número de Órdenes` | Entero | Cuenta todas las órdenes de cabecera, incluidas las que no tienen detalle. | `COUNTROWS ( FactOrdenes )` |
| 3 | `Número de Órdenes con Detalle` | Entero | Órdenes que tienen al menos una línea. | `DISTINCTCOUNT ( FactCompras[PurchaseOrderID] )` |
| 4 | `Valor Promedio por Orden` | Moneda | Monto de líneas por orden con detalle. | `DIVIDE ( [Total Comprado], [Número de Órdenes con Detalle] )` |
| 5 | `Total con Impuestos y Flete` | Moneda | Suma `TotalDue` de cabecera (SubTotal + impuestos + flete). | `SUM ( FactOrdenes[TotalDue] )` |
| 6 | `Valor Promedio por Orden (TotalDue)` | Moneda | `TotalDue` promedio por orden. | `DIVIDE ( [Total con Impuestos y Flete], [Número de Órdenes] )` |
| 7 | `Unidades Compradas` | Entero | Suma de unidades ordenadas. | `SUM ( FactCompras[CantidadOrdenada] )` |
| 8 | `Proveedores con Compras` | Entero | Proveedores distintos con al menos una línea. | `DISTINCTCOUNT ( FactCompras[VendorID] )` |
| 9 | `Proveedores Activos` | Entero | Proveedores activos del maestro, con o sin compras. | `CALCULATE ( DISTINCTCOUNT ( DimProveedor[VendorID] ), DimProveedor[ActiveFlag] = TRUE () )` |
| 10 | `Productos Comprados` | Entero | Productos distintos comprados. | `DISTINCTCOUNT ( FactCompras[ProductID] )` |
| 11 | `Costo Promedio Unitario` | Moneda | Monto comprado por unidad. | `DIVIDE ( [Total Comprado], [Unidades Compradas] )` |
| 12 | `Cantidad Recibida` | Entero | Unidades recibidas. | `SUM ( FactCompras[CantidadRecibida] )` |
| 13 | `Cantidad Rechazada` | Entero | Unidades rechazadas. | `SUM ( FactCompras[CantidadRechazada] )` |
| 14 | `Porcentaje de Rechazo` | Porcentaje | Rechazadas sobre recibidas + rechazadas. | `DIVIDE ( [Cantidad Rechazada], [Cantidad Recibida] + [Cantidad Rechazada] )` |
| 15 | `Órdenes Completadas` | Entero | Órdenes con estado Completada. | `CALCULATE ( [Número de Órdenes], DimEstadoOrden[Estado] = "Completada" )` |
| 16 | `Porcentaje de Órdenes Completadas` | Porcentaje | Completadas sobre total de órdenes. | `DIVIDE ( [Órdenes Completadas], [Número de Órdenes] )` |
| 17 | `Órdenes Pendientes` | Entero | Órdenes con estado Pendiente. | `CALCULATE ( [Número de Órdenes], DimEstadoOrden[Estado] = "Pendiente" )` |
| 18 | `Órdenes Rechazadas` | Entero | Órdenes con estado Rechazada. | `CALCULATE ( [Número de Órdenes], DimEstadoOrden[Estado] = "Rechazada" )` |
| 19 | `Días Promedio de Entrega` | Decimal | Promedio de días entre orden y envío. | `AVERAGEX ( FILTER ( FactOrdenes, NOT ISBLANK ( FactOrdenes[FechaEnvio] ) ), FactOrdenes[DiasEntrega] )` |
| 20 | `Proveedores Preferidos` | Entero | Proveedores preferidos que tienen compras. | `CALCULATE ( DISTINCTCOUNT ( FactCompras[VendorID] ), DimProveedor[PreferredVendorStatus] = TRUE () )` |
| 21 | `Porcentaje de Proveedores Preferidos` | Porcentaje | Preferidos sobre proveedores con compras. | `DIVIDE ( [Proveedores Preferidos], [Proveedores con Compras] )` |
| 22 | `Calificación Crediticia Promedio` | Decimal | Promedio simple por proveedor. | `AVERAGEX ( VALUES ( DimProveedor[VendorID] ), CALCULATE ( AVERAGE ( DimProveedor[CreditRating] ) ) )` |
| 23 | `Monto Promedio por Proveedor` | Moneda | Gasto promedio por proveedor con compras. | `DIVIDE ( [Total Comprado], [Proveedores con Compras] )` |
| 24 | `Órdenes por Proveedor` | Decimal | Órdenes promedio por proveedor con compras. | `DIVIDE ( [Número de Órdenes], [Proveedores con Compras] )` |

### Tarjetas KPI sugeridas para Sebastián

| Tarjeta | Medida | Formato |
|---|---|---|
| Gasto total | `Total Comprado` | Moneda |
| Órdenes | `Número de Órdenes` | Entero |
| Proveedores con compras | `Proveedores con Compras` | Entero |
| Ticket promedio | `Valor Promedio por Orden` | Moneda |
| % órdenes completadas | `Porcentaje de Órdenes Completadas` | Porcentaje |
| % rechazo | `Porcentaje de Rechazo` | Porcentaje |

---

## 3. Medidas avanzadas (carpeta `02 Avanzadas`)

### 3.1 Inteligencia de tiempo

| # | Medida | Formato | Qué calcula | Fórmula |
|---:|---|---|---|---|
| 25 | `Total Comprado Año Anterior` | Moneda | Mismo período del año anterior. | `CALCULATE ( [Total Comprado], SAMEPERIODLASTYEAR ( DimFecha[Date] ) )` |
| 26 | `Variación Porcentual Año Anterior` | Porcentaje | Variación contra el año anterior. | `VAR Actual = [Total Comprado] VAR Anterior = [Total Comprado Año Anterior] RETURN DIVIDE ( Actual - Anterior, Anterior )` |
| 27 | `Total Comprado YTD` | Moneda | Acumulado del año. | `TOTALYTD ( [Total Comprado], DimFecha[Date] )` |
| 28 | `Total Comprado MTD` | Moneda | Acumulado del mes. | `TOTALMTD ( [Total Comprado], DimFecha[Date] )` |
| 29 | `Total Comprado Acumulado` | Moneda | Acumulado corrido sobre el eje de fechas. | `CALCULATE ( [Total Comprado], FILTER ( ALLSELECTED ( DimFecha[Date] ), DimFecha[Date] <= MAX ( DimFecha[Date] ) ) )` |
| 30 | `Variación Porcentual Mes Anterior` | Porcentaje | Variación contra el mes anterior. | `VAR Actual = [Total Comprado] VAR Anterior = CALCULATE ( [Total Comprado], DATEADD ( DimFecha[Date], -1, MONTH ) ) RETURN DIVIDE ( Actual - Anterior, Anterior )` |
| 31 | `Total Comprado por Fecha de Envío` | Moneda | Reasigna el filtro de fecha a la fecha de envío. | `CALCULATE ( [Total Comprado], USERELATIONSHIP ( FactCompras[FechaEnvio], DimFecha[Date] ) )` |
| 32 | `Total Comprado por Fecha de Vencimiento` | Moneda | Reasigna el filtro de fecha a la fecha de vencimiento. | `CALCULATE ( [Total Comprado], USERELATIONSHIP ( FactCompras[FechaVencimiento], DimFecha[Date] ) )` |
| 33 | `Total con Impuestos y Flete Año Anterior` | Moneda | `TotalDue` del mismo período del año anterior. | `CALCULATE ( [Total con Impuestos y Flete], SAMEPERIODLASTYEAR ( DimFecha[Date] ) )` |
| 34 | `Variación Porcentual TotalDue Año Anterior` | Porcentaje | Variación de `TotalDue` contra el año anterior. | `VAR Actual = [Total con Impuestos y Flete] VAR Anterior = [Total con Impuestos y Flete Año Anterior] RETURN DIVIDE ( Actual - Anterior, Anterior )` |

### 3.2 Ranking, participación y concentración

| # | Medida | Formato | Qué calcula | Fórmula |
|---:|---|---|---|---|
| 35 | `Ranking Proveedor` | Entero | Posición del proveedor por gasto. | `RANKX ( ALLSELECTED ( DimProveedor[NombreProveedor] ), [Total Comprado], , DESC, DENSE )` |
| 36 | `Participación del Total (Proveedores)` | Porcentaje | Cuota del proveedor sobre el total visible. | `DIVIDE ( [Total Comprado], CALCULATE ( [Total Comprado], ALLSELECTED ( DimProveedor ) ) )` |
| 37 | `Participación del Total (Tiempo)` | Porcentaje | Cuota del período sobre el total visible. | `DIVIDE ( [Total Comprado], CALCULATE ( [Total Comprado], ALLSELECTED ( DimFecha ) ) )` |
| 38 | `Top 10 Proveedores` | Moneda | Gasto de los 10 proveedores principales. | `CALCULATE ( [Total Comprado], TOPN ( 10, ALLSELECTED ( DimProveedor[NombreProveedor] ), [Total Comprado], DESC ) )` |
| 39 | `Concentración Top 10` | Porcentaje | Peso de los 10 principales sobre el total. | `DIVIDE ( [Top 10 Proveedores], CALCULATE ( [Total Comprado], ALLSELECTED ( DimProveedor ) ) )` |
| 40 | `HHI Proveedores` | Porcentaje | Índice Herfindahl-Hirschman (suma de cuotas al cuadrado). | `VAR TotalGeneral = CALCULATE ( [Total Comprado], ALLSELECTED ( DimProveedor ) ) RETURN SUMX ( ALLSELECTED ( DimProveedor[VendorID] ), VAR CompraProveedor = CALCULATE ( [Total Comprado] ) VAR Cuota = DIVIDE ( CompraProveedor, TotalGeneral ) RETURN Cuota ^ 2 )` |
| 41 | `Participación del Segmento` | Porcentaje | Cuota del segmento sobre el total visible. | `DIVIDE ( [Total Comprado], CALCULATE ( [Total Comprado], ALLSELECTED ( DimProveedor[Segmento] ) ) )` |
| 42 | `Proveedores por Segmento` | Entero | Proveedores con compras en cada segmento. | `DISTINCTCOUNT ( FactCompras[VendorID] )` |
| 43 | `Porcentaje de Proveedores por Segmento` | Porcentaje | Peso del segmento en el total de proveedores. | `DIVIDE ( [Proveedores por Segmento], CALCULATE ( [Proveedores por Segmento], ALLSELECTED ( DimProveedor[Segmento] ) ) )` |
| 44 | `Ranking Producto` | Entero | Posición del producto por gasto. | `RANKX ( ALLSELECTED ( DimProducto[NombreProducto] ), [Total Comprado], , DESC, DENSE )` |
| 45 | `Participación del Total (Productos)` | Porcentaje | Cuota del producto sobre el total visible. | `DIVIDE ( [Total Comprado], CALCULATE ( [Total Comprado], ALLSELECTED ( DimProducto ) ) )` |
| 46 | `Compra Acumulada Proveedor` | Moneda | Gasto acumulado de proveedores con compra >= al actual. | `VAR ProveedorActual = MAX ( DimProveedor[VendorID] ) VAR CompraActual = CALCULATE ( [Total Comprado], DimProveedor[VendorID] = ProveedorActual ) RETURN SUMX ( FILTER ( ALLSELECTED ( DimProveedor[VendorID] ), CALCULATE ( [Total Comprado] ) >= CompraActual ), CALCULATE ( [Total Comprado] ) )` |
| 47 | `Clasificación ABC` | Texto | A: hasta 80 % acumulado; B: hasta 95 %; C: resto. | `VAR TotalGeneral = CALCULATE ( [Total Comprado], ALLSELECTED ( DimProveedor ) ) VAR Acumulado = [Compra Acumulada Proveedor] VAR Porcentaje = DIVIDE ( Acumulado, TotalGeneral ) RETURN SWITCH ( TRUE (), ISBLANK ( [Total Comprado] ), BLANK (), Porcentaje <= 0.80, "A", Porcentaje <= 0.95, "B", "C" )` |

### 3.3 Comportamiento y calidad del proveedor

| # | Medida | Formato | Qué calcula | Fórmula |
|---:|---|---|---|---|
| 48 | `Proveedores Nuevos` | Entero | Proveedores cuya primera compra cae en el período visible. | `VAR FechaInicio = MIN ( DimFecha[Date] ) VAR FechaFin = MAX ( DimFecha[Date] ) VAR PrimeraCompra = ADDCOLUMNS ( ALLSELECTED ( DimProveedor[VendorID] ), "@PrimeraCompra", CALCULATE ( MIN ( FactCompras[FechaOrden] ), ALL ( DimFecha ) ) ) RETURN COUNTROWS ( FILTER ( PrimeraCompra, [@PrimeraCompra] >= FechaInicio && [@PrimeraCompra] <= FechaFin ) )` |
| 49 | `Proveedores sin Compra en el Periodo` | Entero | Proveedores del maestro sin compras en el período. | `COUNTROWS ( FILTER ( ALLSELECTED ( DimProveedor[VendorID] ), ISBLANK ( CALCULATE ( [Total Comprado] ) ) ) )` |
| 50 | `Días desde Última Compra` | Entero | Días transcurridos desde la última compra histórica. | `VAR UltimaCompra = CALCULATE ( MAX ( FactCompras[FechaOrden] ), ALL ( DimFecha ) ) RETURN IF ( ISBLANK ( UltimaCompra ), BLANK (), DATEDIFF ( UltimaCompra, TODAY (), DAY ) )` |
| 51 | `Semáforo Proveedor` | Texto | Verde/amarillo/rojo según recencia y monto. | `VAR Dias = [Días desde Última Compra] VAR Compra = [Total Comprado] RETURN SWITCH ( TRUE (), ISBLANK ( Compra ), "Sin compras", ISBLANK ( Dias ), "Sin fecha", Dias <= 90 && Compra >= 100000, "Verde", Dias <= 180, "Amarillo", "Rojo" )` |
| 52 | `Tasa de Cumplimiento` | Porcentaje | Unidades recibidas sobre ordenadas. | `DIVIDE ( SUM ( FactCompras[CantidadRecibida] ), SUM ( FactCompras[CantidadOrdenada] ) )` |
| 53 | `Días de Entrega Ponderados` | Decimal | Días de entrega ponderados por cantidad. | `VAR Filas = FILTER ( FactCompras, NOT ISBLANK ( FactCompras[FechaEnvio] ) ) RETURN DIVIDE ( SUMX ( Filas, DATEDIFF ( FactCompras[FechaOrden], FactCompras[FechaEnvio], DAY ) * FactCompras[CantidadOrdenada] ), SUMX ( Filas, FactCompras[CantidadOrdenada] ) )` |
| 54 | `Monto Rechazado Estimado` | Moneda | Valor prorrateado de las unidades rechazadas. | `SUMX ( FactCompras, DIVIDE ( FactCompras[CantidadRechazada], FactCompras[CantidadOrdenada] ) * FactCompras[TotalLinea] )` |
| 55 | `Porcentaje de Monto Rechazado` | Porcentaje | Monto rechazado sobre total comprado. | `DIVIDE ( [Monto Rechazado Estimado], [Total Comprado] )` |
| 56 | `Proveedores con Rechazo` | Entero | Proveedores con al menos una unidad rechazada. | `CALCULATE ( DISTINCTCOUNT ( FactCompras[VendorID] ), FactCompras[CantidadRechazada] > 0 )` |
| 57 | `Porcentaje de Proveedores con Rechazo` | Porcentaje | Proveedores con rechazo sobre proveedores con compras. | `DIVIDE ( [Proveedores con Rechazo], [Proveedores con Compras] )` |

### 3.4 Control de calidad y ventanas móviles (carpeta `03 Órdenes`)

| # | Medida | Formato | Qué calcula | Fórmula |
|---:|---|---|---|---|
| 58 | `Órdenes sin Detalle` | Entero | Diferencia entre órdenes de cabecera y órdenes con líneas. | `[Número de Órdenes] - [Número de Órdenes con Detalle]` |
| 59 | `Diferencia TotalDue vs Líneas` | Moneda | Diferencia entre `TotalDue` y la suma de líneas. | `[Total con Impuestos y Flete] - [Total Comprado]` |
| 60 | `Porcentaje de Diferencia TotalDue vs Líneas` | Porcentaje | Diferencia relativa sobre el total comprado. | `DIVIDE ( [Diferencia TotalDue vs Líneas], [Total Comprado] )` |
| 61 | `Total Comprado Últimos 12 Meses` | Moneda | Ventana móvil de 12 meses. | `CALCULATE ( [Total Comprado], DATESINPERIOD ( DimFecha[Date], MAX ( DimFecha[Date] ), -12, MONTH ) )` |
| 62 | `Proveedores Activos Últimos 12 Meses` | Entero | Proveedores con compras en los últimos 12 meses. | `CALCULATE ( [Proveedores con Compras], DATESINPERIOD ( DimFecha[Date], MAX ( DimFecha[Date] ), -12, MONTH ) )` |

---

## 4. Notas de uso

1. **`[Número de Órdenes]` vs `[Número de Órdenes con Detalle]`.** La primera cuenta las 4.015 órdenes de cabecera; la segunda, las 4.013 con líneas. Para visuales por producto usa la segunda, porque `FactOrdenes` no tiene relación con `DimProducto`.
2. **`[Total Comprado]` vs `[Total con Impuestos y Flete]`.** No son intercambiables. La primera suma `LineTotal`; la segunda suma `TotalDue` de cabecera. No las sumes en la misma tarjeta.
3. **Medidas de tiempo.** Requieren que `DimFecha` esté marcada como tabla de fechas y que la relación activa sea `DimFecha[Date] → FactCompras[FechaOrden]` (y la equivalente en `FactOrdenes`).
4. **Relaciones inactivas.** `[Total Comprado por Fecha de Envío]` y `[Total Comprado por Fecha de Vencimiento]` requieren las relaciones inactivas indicadas en `docs/criterio3_modelo_estrella.md`.
5. **Medidas a nivel de proveedor.** `[Ranking Proveedor]`, `[Compra Acumulada Proveedor]`, `[Clasificación ABC]`, `[Días desde Última Compra]` y `[Semáforo Proveedor]` están pensadas para tablas o gráficos con `DimProveedor[NombreProveedor]` en el eje o en las filas.
6. **`TODAY()`.** `[Días desde Última Compra]` y `[Semáforo Proveedor]` usan la fecha actual del equipo. Si se abre el `.pbix` en otra fecha, el resultado cambia; es lo esperado.
7. **Umbral del semáforo.** El umbral de 100.000 y los 90/180 días son una regla de ejemplo. Ajustarlos según la política de compras.
8. **Segmentos.** Las medidas de segmento devuelven `Sin segmento` si no se cargó `bi.VendorSegmento`. Ver `src/load_vendor_segments.py`.

---

## 5. Validación de las medidas principales

| Medida | Valor esperado |
|---|---:|
| `Total Comprado` | 63.792.094,84 |
| `Total con Impuestos y Flete` | 70.486.331,59 |
| `Número de Órdenes` | 4.015 |
| `Número de Órdenes con Detalle` | 4.013 |
| `Proveedores con Compras` | 86 |
| `Productos Comprados` | 266 |
| `Unidades Compradas` | 2.348.638 |
| `Cantidad Recibida` | 2.327.299 |
| `Cantidad Rechazada` | 72.700 |
| `Órdenes Completadas` | 3.688 |
| `Órdenes Pendientes` | 229 |
| `Órdenes Rechazadas` | 86 |
| `Órdenes sin Detalle` | 2 |
| `Diferencia TotalDue vs Líneas` | 6.694.236,75 |

Si alguna medida no coincide, revisar primero las relaciones y los filtros de fecha; después, que las vistas `bi` estén actualizadas.
