from pathlib import Path

import pandas as pd
from db import crear_conexion


# Ruta raíz del proyecto
RAIZ_PROYECTO = Path(__file__).resolve().parent.parent
CARPETA_DATOS = RAIZ_PROYECTO / "data" / "raw"

# Crear la conexión con SQL Server
engine = crear_conexion()

# Tablas que vamos a extraer
consultas = {
    "vendor": """
        SELECT
        BusinessEntityID,
        Name,
        CreditRating,
        PreferredVendorStatus,
        ActiveFlag
        FROM Purchasing.Vendor
    """,
    "purchase_order_header": """
        SELECT *
        FROM Purchasing.PurchaseOrderHeader
    """,
    "purchase_order_detail": """
        SELECT *
        FROM Purchasing.PurchaseOrderDetail
    """,
    "product_vendor": """
        SELECT *
        FROM Purchasing.ProductVendor
    """,
    "ship_method": """
        SELECT *
        FROM Purchasing.ShipMethod
    """,
    "product": """
        SELECT
            ProductID,
            Name,
            ProductNumber,
            MakeFlag,
            FinishedGoodsFlag,
            StandardCost,
            ListPrice,
            ProductSubcategoryID,
            ProductModelID
        FROM Production.Product
    """,
}

try:
    # Asegurar que exista la carpeta de destino
    CARPETA_DATOS.mkdir(parents=True, exist_ok=True)

    for nombre, consulta in consultas.items():
        print(f"\nExtrayendo tabla: {nombre}...")

        # Consultar SQL Server y cargar los datos en pandas
        df = pd.read_sql(consulta, engine)

        # Guardar los datos como CSV
        ruta_csv = CARPETA_DATOS / f"{nombre}.csv"
        df.to_csv(ruta_csv, index=False, encoding="utf-8-sig")

        print(f"Archivo guardado: {ruta_csv}")
        print(f"Filas: {df.shape[0]} | Columnas: {df.shape[1]}")

    print("\n¡Extracción finalizada!")

finally:
    engine.dispose()

