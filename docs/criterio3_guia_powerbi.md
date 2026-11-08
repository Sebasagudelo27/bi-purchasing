# Guía paso a paso — Construir `Compras_v1_Molina.pbix`

**Proyecto:** BI Purchasing — AdventureWorks2  
**Responsable:** Molina  
**Objetivo:** conectar Power BI Desktop a las vistas del esquema `bi`, armar el modelo en estrella, agregar las medidas y guardar el archivo para Sebastián.

> Esta guía asume que `sql/01_modelo_estrella.sql` ya se ejecutó en la base `AdventureWorks2`. Las vistas `bi.*` ya existen y están validadas.

---

## 0. Antes de empezar

| Requisito | Detalle |
|---|---|
| Power BI Desktop | Versión reciente (2024 o superior). |
| Conexión | Azure SQL Database `sebastian-sql-server-2026.database.windows.net`, base `AdventureWorks2`. |
| Credenciales | Usuario y contraseña de SQL Server. No guardarlas en el repositorio. |
| Archivos de apoyo | `powerbi/medidas_basicas.dax`, `powerbi/medidas_avanzadas.dax`. |
| Tiempo estimado | 30–45 minutos. |

---

## 1. Abrir Power BI Desktop y conectar

1. Abrir **Power BI Desktop**.
2. Ir a **Inicio → Obtener datos → Más… → Azure → Azure SQL Database**.
3. Completar:
   - **Servidor:** `sebastian-sql-server-2026.database.windows.net`
   - **Base de datos:** `AdventureWorks2`
   - **Modo de conectividad:** Importar (recomendado para el `.pbix`).
4. En **Autenticación**, elegir **Base de datos** e ingresar el usuario y la contraseña de SQL.
5. Clic en **Conectar**.

> Si aparece un aviso de cifrado, elegir **Cifrar** y **Aceptar**. La base usa `Encrypt=True` y `TrustServerCertificate=False`.

---

## 2. Seleccionar las vistas

En el **Navegador**:

1. Desplegar la base `AdventureWorks2`.
2. Buscar el esquema `bi`.
3. Marcar estas vistas:
   - `bi.DimProveedor`
   - `bi.DimProducto`
   - `bi.DimFecha`
   - `bi.DimMetodoEnvio`
   - `bi.DimEstadoOrden`
   - `bi.FactCompras`
   - `bi.FactOrdenes`
4. Verificar que se muestre una vista previa con datos.
5. Clic en **Cargar** (no usar **Transformar datos** salvo que se quiera revisar tipos).

> Si no aparece el esquema `bi`, confirmar que el script SQL se ejecutó en la base correcta y que el usuario tiene permiso de lectura sobre el esquema.

---

## 3. Revisar tipos de datos

En la vista **Modelo** o **Datos**, confirmar:

| Columna | Tipo esperado |
|---|---|
| `DimFecha[Date]`, `FactCompras[FechaOrden]`, `FactCompras[FechaEnvio]`, `FactCompras[FechaVencimiento]`, `FactOrdenes[FechaOrden]`, `FactOrdenes[FechaEnvio]` | Fecha |
| `TotalLinea`, `PrecioUnitario`, `SubTotal`, `TaxAmt`, `Freight`, `TotalDue`, `CostoEstandar`, `PrecioLista`, `ShipBase`, `ShipRate` | Número decimal fijo (moneda) |
| `CantidadOrdenada`, `CantidadRecibida`, `CantidadRechazada`, `CantidadEnStock`, `DiasEntrega` | Número entero / decimal |
| `VendorID`, `ProductID`, `ShipMethodID`, `Status`, `PurchaseOrderID` | Número entero |

Si alguna columna de fecha llegó como texto, usar **Transformar datos → Tipo de dato → Fecha**.

---

## 4. Crear las relaciones

Ir a la vista **Modelo**. Crear las relaciones arrastrando la clave de la dimensión hacia la clave del hecho.

| Desde (1) | Hacia (*) | Activa |
|---|---|---|
| `DimProveedor[VendorID]` | `FactCompras[VendorID]` | Sí |
| `DimProveedor[VendorID]` | `FactOrdenes[VendorID]` | Sí |
| `DimProducto[ProductID]` | `FactCompras[ProductID]` | Sí |
| `DimMetodoEnvio[ShipMethodID]` | `FactCompras[ShipMethodID]` | Sí |
| `DimMetodoEnvio[ShipMethodID]` | `FactOrdenes[ShipMethodID]` | Sí |
| `DimEstadoOrden[Status]` | `FactCompras[Status]` | Sí |
| `DimEstadoOrden[Status]` | `FactOrdenes[Status]` | Sí |
| `DimFecha[Date]` | `FactCompras[FechaOrden]` | Sí |
| `DimFecha[Date]` | `FactOrdenes[FechaOrden]` | Sí |
| `DimFecha[Date]` | `FactCompras[FechaEnvio]` | **No** |
| `DimFecha[Date]` | `FactCompras[FechaVencimiento]` | **No** |
| `DimFecha[Date]` | `FactOrdenes[FechaEnvio]` | **No** |

Para las relaciones inactivas:

1. Crear la relación normalmente.
2. En **Editar relación**, desmarcar **Activa**.
3. Verificar que la cardinalidad sea **1 a varios** y la dirección de filtro **Simple**.

> No crear relaciones entre `FactCompras` y `FactOrdenes` directamente. Ambas se conectan a través de las dimensiones. Si se relacionan entre sí, se pueden producir ambigüedades y filtros inesperados.

---

## 5. Marcar `DimFecha` como tabla de fechas

1. Ir a la vista **Datos** o **Modelo**.
2. Seleccionar la tabla `DimFecha`.
3. En la cinta, clic en **Marcar como tabla de fechas**.
4. Elegir la columna `Date`.
5. Aceptar.

Sin este paso, las medidas `SAMEPERIODLASTYEAR`, `TOTALYTD`, `TOTALMTD` y `DATEADD` pueden dar resultados incorrectos.

---

## 6. Ocultar claves y ordenar columnas

### 6.1 Ocultar columnas técnicas

En la vista **Modelo**, clic derecho → **Ocultar** en:

- `FactCompras`: `OrdenLineaID`, `PurchaseOrderID`, `PurchaseOrderDetailID`, `VendorID`, `ProductID`, `ShipMethodID`, `Status`, `FechaModificacion`.
- `FactOrdenes`: `PurchaseOrderID`, `VendorID`, `ShipMethodID`, `Status`, `FechaModificacion`.
- `DimProveedor`: `VendorID`, `AccountNumber`, `PurchasingWebServiceURL`, `Email`, `TipoDireccion`, `SegmentoEsEstimado`.
- `DimProducto`: `ProductID`, `ProductSubcategoryID`.
- `DimMetodoEnvio`: `ShipMethodID`.
- `DimEstadoOrden`: `Status`, `EstadoIngles`, `Orden`.

> Las claves se ocultan para el usuario final, pero siguen disponibles para las relaciones y las medidas.

### 6.2 Ordenar columnas descriptivas

Seleccionar la columna → **Herramientas de columna → Ordenar por columna**:

| Columna | Ordenar por |
|---|---|
| `DimFecha[Mes]` | `DimFecha[MesNúmero]` |
| `DimFecha[AñoMes]` | `DimFecha[AñoMesNúmero]` |
| `DimFecha[DíaSemana]` | `DimFecha[DíaSemanaNúmero]` |
| `DimFecha[Trimestre]` | `DimFecha[TrimestreNúmero]` |
| `DimEstadoOrden[Estado]` | `DimEstadoOrden[Orden]` |

### 6.3 Formatos

| Columna / medida | Formato |
|---|---|
| Montos (`TotalLinea`, `TotalDue`, `SubTotal`, `TaxAmt`, `Freight`, `PrecioUnitario`, `CostoEstandar`, `PrecioLista`) | Moneda / `$ #,##0.00` |
| Porcentajes | `0.0 %` |
| Fechas | `dd/MM/yyyy` |
| Cantidades | Número entero o decimal según la columna |

---

## 7. Crear la tabla `_Medidas`

1. **Inicio → Escribir datos**.
2. Nombre: `_Medidas`.
3. Crear una columna llamada `Valor` (tipo Texto) y una fila vacía.
4. Cargar.
5. Ocultar la columna `Valor` y la tabla en la vista de campos si se desea.

Las medidas se agregan con **clic derecho en `_Medidas` → Nueva medida**.

---

## 8. Agregar las medidas

### 8.1 Medidas básicas (prioridad para las tarjetas KPI)

Abrir `powerbi/medidas_basicas.dax` y agregar las 24 medidas. Para cada una:

1. Clic derecho en `_Medidas` → **Nueva medida**.
2. Pegar la expresión (solo lo que está después del `=`).
3. Asignar el nombre exacto.
4. En **Propiedades → Carpeta de presentación**, escribir `01 Básicas`.
5. Aplicar el formato indicado.

### 8.2 Medidas avanzadas

Repetir el proceso con `powerbi/medidas_avanzadas.dax`. Usar las carpetas:

- `02 Avanzadas` para tiempo, ranking, concentración, comportamiento y ventanas móviles.
- `03 Órdenes` para `Órdenes sin Detalle`, `Diferencia TotalDue vs Líneas` y `Porcentaje de Diferencia TotalDue vs Líneas`.

> Si una medida muestra error, revisar que el nombre de la tabla y de la columna coincidan exactamente con el modelo. Los nombres distinguen mayúsculas, tildes y espacios.

---

## 9. Página de validación (opcional pero recomendada)

Crear una página llamada **Validación** con:

### 9.1 Tarjetas KPI

| Tarjeta | Medida | Valor esperado |
|---|---|---:|
| Gasto total | `Total Comprado` | 63.792.094,84 |
| Órdenes | `Número de Órdenes` | 4.015 |
| Proveedores con compras | `Proveedores con Compras` | 86 |
| Ticket promedio | `Valor Promedio por Orden` | ~15.896 |
| % completadas | `Porcentaje de Órdenes Completadas` | ~91,9 % |
| % rechazo | `Porcentaje de Rechazo` | ~3,0 % |

### 9.2 Tabla de control

Agregar una tabla con:

- `DimEstadoOrden[Estado]`
- `Número de Órdenes`
- `Total con Impuestos y Flete`

Valores esperados:

| Estado | Órdenes | TotalDue |
|---|---:|---:|
| Completada | 3.688 | 62.785.395,45 |
| Pendiente | 229 | 3.881.645,68 |
| Aprobada | 12 | 2.380.772,81 |
| Rechazada | 86 | 1.438.517,64 |

### 9.3 Control de exclusión

Agregar una tarjeta con:

```dax
Prueba 1699 y 1700 =
COUNTROWS (
    FILTER (
        FactCompras,
        FactCompras[VendorID] IN { 1699, 1700 }
    )
)
```

Debe mostrar **0**.

---

## 10. Guardar el archivo

1. **Archivo → Guardar como**.
2. Nombre: `Compras_v1_Molina.pbix`.
3. Guardar en una carpeta local del proyecto (no en `data/raw` ni en una carpeta sincronizada con credenciales).
4. Cerrar y volver a abrir para confirmar que el modelo carga sin errores.

> Si Power BI pregunta por las credenciales al reabrir, elegir **Base de datos** y volver a ingresarlas. No guardar la contraseña en el `.pbix` si el archivo se va a compartir.

---

## 11. Entregar a Sebastián

Enviar:

- `Compras_v1_Molina.pbix`.
- `docs/criterio3_modelo_estrella.md`.
- `docs/criterio3_medidas_dax.md`.
- `docs/criterio3_guia_powerbi.md`.
- `powerbi/medidas_basicas.dax`.
- `powerbi/medidas_avanzadas.dax`.

Mensaje sugerido:

> Sebastián: te paso `Compras_v1_Molina.pbix` con el modelo en estrella validado. Las tarjetas KPI pueden usar las medidas de la carpeta `01 Básicas`. Para análisis de tiempo, ranking y concentración están las de `02 Avanzadas`. La documentación del modelo y los valores esperados están en `docs/criterio3_modelo_estrella.md` y `docs/criterio3_medidas_dax.md`. Cualquier duda de relaciones, avísame.

---

## 12. Solución de problemas

| Síntoma | Causa probable | Solución |
|---|---|---|
| No aparece el esquema `bi` | El script no se ejecutó en `AdventureWorks2` o el usuario no tiene permiso. | Ejecutar `sql/01_modelo_estrella.sql` y verificar permisos. |
| Error de credenciales | Autenticación incorrecta o base equivocada. | Revisar servidor, base y usuario; usar **Base de datos**, no **Windows**. |
| Una relación no se puede crear | Tipos distintos (por ejemplo `int` vs `tinyint`). | Verificar tipos; en el modelo ya están alineados (`Status` es `tinyint` en dimensiones y hechos). |
| `SAMEPERIODLASTYEAR` da vacío | `DimFecha` no está marcada como tabla de fechas o la relación no está activa. | Marcar `DimFecha` y revisar la relación `DimFecha[Date] → FactCompras[FechaOrden]`. |
| `[Total Comprado]` no coincide | Filtro de fecha, relación faltante o vista desactualizada. | Comparar con la sección 8 de `docs/criterio3_modelo_estrella.md`. |
| `[Número de Órdenes]` da 4.013 en vez de 4.015 | Se está usando `FactCompras` en lugar de `FactOrdenes`. | Usar la medida `[Número de Órdenes]`, que se calcula sobre `FactOrdenes`. |
| `[Días desde Última Compra]` da valores raros en una tarjeta | Es una medida a nivel de proveedor. | Usarla en una tabla con `DimProveedor[NombreProveedor]`. |
| Los segmentos muestran `Sin segmento` | No se cargó `bi.VendorSegmento`. | Ejecutar `python src/load_vendor_segments.py` y actualizar `DimProveedor`. |

---

## 13. Checklist final

- [ ] Conexión a `AdventureWorks2` creada.
- [ ] 7 vistas del esquema `bi` cargadas.
- [ ] 12 relaciones creadas (9 activas + 3 inactivas).
- [ ] `DimFecha` marcada como tabla de fechas.
- [ ] Claves ocultas.
- [ ] Formatos y orden de columnas ajustados.
- [ ] Tabla `_Medidas` creada.
- [ ] 24 medidas básicas agregadas.
- [ ] 38 medidas avanzadas agregadas.
- [ ] Página de validación con los valores esperados.
- [ ] `Compras_v1_Molina.pbix` guardado y reabierto sin errores.
- [ ] Archivo y documentación enviados a Sebastián.
