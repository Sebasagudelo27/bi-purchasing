/* ============================================================================
   CRITERIO 3 - MODELO EN ESTRELLA PARA POWER BI
   Proyecto: BI Purchasing - AdventureWorks2
   Responsable: Molina
   ----------------------------------------------------------------------------
   Este script crea el esquema `bi` con las vistas que Power BI Desktop debe
   importar. El modelo deja:
     - 1 dimension de proveedor (sin los proveedores de prueba 1699 y 1700)
     - 1 dimension de producto
     - 1 dimension de fecha
     - 1 dimension de metodo de envio
     - 1 dimension de estado de orden
     - 2 tablas de hechos:
         * bi.FactCompras  -> grano: linea de orden (para producto/cantidades)
         * bi.FactOrdenes  -> grano: orden (para conteo de ordenes/TotalDue)

   Por que dos hechos: TotalDue, SubTotal, TaxAmt y Freight viven en la
   cabecera de la orden. Si se repiten en cada linea, al sumarlos se duplican.
   Separando los hechos se evita ese error y se puede analizar la orden completa
   sin inflar los montos por producto.

   Ejecutar conectado a la base AdventureWorks2. El script es idempotente:
   se puede volver a ejecutar sin borrar datos.
   ============================================================================ */

IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'bi')
    EXEC('CREATE SCHEMA bi');
GO

/* ----------------------------------------------------------------------------
   Tabla auxiliar para los segmentos de proveedores (K-Means).
   Se puede cargar con src/load_vendor_segments.py.
   Si esta vacia, DimProveedor muestra 'Sin segmento'.
   ---------------------------------------------------------------------------- */
IF OBJECT_ID('bi.VendorSegmento', 'U') IS NULL
BEGIN
    CREATE TABLE bi.VendorSegmento
    (
        VendorID   int          NOT NULL CONSTRAINT PK_VendorSegmento PRIMARY KEY,
        Segmento   nvarchar(50) NOT NULL,
        EsEstimado bit          NOT NULL CONSTRAINT DF_VendorSegmento_EsEstimado DEFAULT (0),
        FechaCarga datetime2(0) NOT NULL CONSTRAINT DF_VendorSegmento_FechaCarga DEFAULT (SYSUTCDATETIME())
    );
END;
GO

/* ============================================================================
   DIMENSIONES
   ============================================================================ */

/* ----------------------------------------------------------------------------
   DimFecha: calendario 2022-01-01 a 2027-12-31.
   Cubre el rango de ordenes (2022-04-15 a 2026-09-30) y un ano adicional
   para comparaciones interanuales.
   ---------------------------------------------------------------------------- */
CREATE OR ALTER VIEW bi.DimFecha
AS
WITH Fechas AS
(
    SELECT DATEADD(DAY, value, CAST('2022-01-01' AS date)) AS Fecha
    FROM GENERATE_SERIES
    (
        0,
        DATEDIFF(DAY, CAST('2022-01-01' AS date), CAST('2027-12-31' AS date))
    )
)
SELECT
    Fecha                                                                   AS [Date],
    YEAR(Fecha)                                                             AS [Año],
    DATEPART(QUARTER, Fecha)                                                AS [TrimestreNúmero],
    'T' + CAST(DATEPART(QUARTER, Fecha) AS varchar(1))                      AS [Trimestre],
    MONTH(Fecha)                                                            AS [MesNúmero],
    CASE MONTH(Fecha)
        WHEN 1  THEN 'Enero'
        WHEN 2  THEN 'Febrero'
        WHEN 3  THEN 'Marzo'
        WHEN 4  THEN 'Abril'
        WHEN 5  THEN 'Mayo'
        WHEN 6  THEN 'Junio'
        WHEN 7  THEN 'Julio'
        WHEN 8  THEN 'Agosto'
        WHEN 9  THEN 'Septiembre'
        WHEN 10 THEN 'Octubre'
        WHEN 11 THEN 'Noviembre'
        WHEN 12 THEN 'Diciembre'
    END                                                                     AS [Mes],
    FORMAT(Fecha, 'yyyy-MM')                                                AS [AñoMes],
    YEAR(Fecha) * 100 + MONTH(Fecha)                                        AS [AñoMesNúmero],
    DAY(Fecha)                                                              AS [Día],
    CASE (DATEDIFF(DAY, CAST('2022-01-01' AS date), Fecha) % 7)
        WHEN 0 THEN 'Sábado'
        WHEN 1 THEN 'Domingo'
        WHEN 2 THEN 'Lunes'
        WHEN 3 THEN 'Martes'
        WHEN 4 THEN 'Miércoles'
        WHEN 5 THEN 'Jueves'
        WHEN 6 THEN 'Viernes'
    END                                                                     AS [DíaSemana],
    ((DATEDIFF(DAY, CAST('2022-01-01' AS date), Fecha) % 7) + 5) % 7 + 1    AS [DíaSemanaNúmero],
    CASE WHEN ((DATEDIFF(DAY, CAST('2022-01-01' AS date), Fecha) % 7) + 5) % 7 + 1 <= 5
         THEN 1 ELSE 0 END                                                  AS [EsDíaHábil],
    CASE WHEN ((DATEDIFF(DAY, CAST('2022-01-01' AS date), Fecha) % 7) + 5) % 7 + 1 >= 6
         THEN 1 ELSE 0 END                                                  AS [EsFinDeSemana]
FROM Fechas;
GO

/* ----------------------------------------------------------------------------
   DimProveedor: una fila por proveedor real (excluye 1699 y 1700).
   Toma la direccion principal (Main Office) y, si existe, el segmento K-Means.
   ---------------------------------------------------------------------------- */
CREATE OR ALTER VIEW bi.DimProveedor
AS
WITH Direccion AS
(
    SELECT
        BusinessEntityID,
        AddressType,
        AddressLine1,
        City,
        StateProvinceName,
        PostalCode,
        CountryRegionName,
        ROW_NUMBER() OVER
        (
            PARTITION BY BusinessEntityID
            ORDER BY
                CASE WHEN AddressType = 'Main Office' THEN 0 ELSE 1 END,
                AddressLine1
        ) AS rn
    FROM Purchasing.vVendorWithAddresses
)
SELECT
    v.BusinessEntityID          AS VendorID,
    v.AccountNumber,
    v.Name                      AS NombreProveedor,
    v.CreditRating,
    v.PreferredVendorStatus,
    v.ActiveFlag,
    v.PurchasingWebServiceURL,
    v.Email,
    d.AddressType               AS TipoDireccion,
    d.AddressLine1              AS Direccion,
    d.City                      AS Ciudad,
    d.StateProvinceName         AS Provincia,
    d.PostalCode                AS CodigoPostal,
    d.CountryRegionName         AS Pais,
    COALESCE(s.Segmento, 'Sin segmento') AS Segmento,
    COALESCE(s.EsEstimado, 0)   AS SegmentoEsEstimado
FROM Purchasing.Vendor AS v
LEFT JOIN Direccion AS d
       ON d.BusinessEntityID = v.BusinessEntityID
      AND d.rn = 1
LEFT JOIN bi.VendorSegmento AS s
       ON s.VendorID = v.BusinessEntityID
WHERE v.BusinessEntityID NOT IN (1699, 1700);
GO

/* ----------------------------------------------------------------------------
   DimProducto: producto + subcategoria + categoria.
   ---------------------------------------------------------------------------- */
CREATE OR ALTER VIEW bi.DimProducto
AS
SELECT
    p.ProductID                 AS ProductID,
    p.Name                      AS NombreProducto,
    p.ProductNumber             AS NumeroProducto,
    p.MakeFlag,
    p.FinishedGoodsFlag,
    p.Color                     AS Color,
    p.Size                      AS Talla,
    p.ProductLine               AS LineaProducto,
    p.Class                     AS Clase,
    p.Style                     AS Estilo,
    p.DaysToManufacture         AS DiasFabricacion,
    p.StandardCost              AS CostoEstandar,
    p.ListPrice                 AS PrecioLista,
    p.ProductSubcategoryID,
    COALESCE(sc.Name, 'Sin subcategoría') AS Subcategoria,
    COALESCE(c.Name, 'Sin categoría')     AS Categoria,
    p.SellStartDate,
    p.SellEndDate,
    p.DiscontinuedDate
FROM Production.Product AS p
LEFT JOIN Production.ProductSubcategory AS sc
       ON sc.ProductSubcategoryID = p.ProductSubcategoryID
LEFT JOIN Production.ProductCategory AS c
       ON c.ProductCategoryID = sc.ProductCategoryID;
GO

/* ----------------------------------------------------------------------------
   DimMetodoEnvio
   ---------------------------------------------------------------------------- */
CREATE OR ALTER VIEW bi.DimMetodoEnvio
AS
SELECT
    ShipMethodID,
    Name        AS MetodoEnvio,
    ShipBase,
    ShipRate
FROM Purchasing.ShipMethod;
GO

/* ----------------------------------------------------------------------------
   DimEstadoOrden: traduccion de los Status de PurchaseOrderHeader.
   ---------------------------------------------------------------------------- */
CREATE OR ALTER VIEW bi.DimEstadoOrden
AS
SELECT
    CAST(v.Status AS tinyint) AS Status,
    v.Estado,
    v.EstadoIngles,
    CAST(v.Orden AS tinyint)  AS Orden
FROM (VALUES
    (1, 'Pendiente',  'Pending',  1),
    (2, 'Aprobada',   'Approved', 2),
    (3, 'Rechazada',  'Rejected', 3),
    (4, 'Completada', 'Complete', 4)
) AS v (Status, Estado, EstadoIngles, Orden);
GO

/* ============================================================================
   TABLAS DE HECHOS
   ============================================================================ */

/* ----------------------------------------------------------------------------
   FactCompras: una fila por linea de PurchaseOrderDetail.
   Excluye las ordenes de los proveedores de prueba 1699 y 1700.
   No incluye TotalDue/SubTotal/TaxAmt/Freight porque son de cabecera y se
   duplicarian al repetirse en cada linea.
   ---------------------------------------------------------------------------- */
CREATE OR ALTER VIEW bi.FactCompras
AS
SELECT
    CAST(h.PurchaseOrderID AS varchar(10)) + '-' +
    CAST(d.PurchaseOrderDetailID AS varchar(10)) AS OrdenLineaID,
    h.PurchaseOrderID,
    d.PurchaseOrderDetailID,
    h.VendorID,
    d.ProductID,
    h.ShipMethodID,
    h.Status,
    CAST(h.OrderDate AS date)   AS FechaOrden,
    CAST(d.DueDate AS date)     AS FechaVencimiento,
    CAST(h.ShipDate AS date)    AS FechaEnvio,
    d.OrderQty                  AS CantidadOrdenada,
    d.UnitPrice                 AS PrecioUnitario,
    d.LineTotal                 AS TotalLinea,
    d.ReceivedQty               AS CantidadRecibida,
    d.RejectedQty               AS CantidadRechazada,
    d.StockedQty                AS CantidadEnStock,
    d.ModifiedDate              AS FechaModificacion
FROM Purchasing.PurchaseOrderHeader AS h
JOIN Purchasing.PurchaseOrderDetail AS d
     ON d.PurchaseOrderID = h.PurchaseOrderID
WHERE h.VendorID NOT IN (1699, 1700);
GO

/* ----------------------------------------------------------------------------
   FactOrdenes: una fila por PurchaseOrderHeader.
   Excluye las ordenes de los proveedores de prueba 1699 y 1700.
   Incluye ordenes sin detalle (6013 y 7013) para que el conteo de ordenes
   y el TotalDue sean exactos.
   ---------------------------------------------------------------------------- */
CREATE OR ALTER VIEW bi.FactOrdenes
AS
SELECT
    h.PurchaseOrderID,
    h.VendorID,
    h.ShipMethodID,
    h.Status,
    CAST(h.OrderDate AS date)   AS FechaOrden,
    CAST(h.ShipDate AS date)    AS FechaEnvio,
    h.SubTotal,
    h.TaxAmt,
    h.Freight,
    h.TotalDue,
    CASE
        WHEN h.ShipDate IS NOT NULL
        THEN DATEDIFF(DAY, h.OrderDate, h.ShipDate)
    END                         AS DiasEntrega,
    h.ModifiedDate              AS FechaModificacion
FROM Purchasing.PurchaseOrderHeader AS h
WHERE h.VendorID NOT IN (1699, 1700);
GO

/* ============================================================================
   VERIFICACION RAPIDA
   Ejecutar despues del script para confirmar los conteos esperados.
   ============================================================================ */
SELECT 'DimProveedor' AS Objeto, COUNT(*) AS Filas FROM bi.DimProveedor
UNION ALL SELECT 'DimProducto', COUNT(*) FROM bi.DimProducto
UNION ALL SELECT 'DimFecha', COUNT(*) FROM bi.DimFecha
UNION ALL SELECT 'DimMetodoEnvio', COUNT(*) FROM bi.DimMetodoEnvio
UNION ALL SELECT 'DimEstadoOrden', COUNT(*) FROM bi.DimEstadoOrden
UNION ALL SELECT 'FactCompras', COUNT(*) FROM bi.FactCompras
UNION ALL SELECT 'FactOrdenes', COUNT(*) FROM bi.FactOrdenes;
GO
