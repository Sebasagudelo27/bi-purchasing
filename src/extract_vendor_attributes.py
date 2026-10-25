"""TASK 6.1.2 - Extrae atributos adicionales de los proveedores (ubicación y datos de contacto)
desde SQL Server y los guarda en data/raw/vendor_attributes.csv.

Uso (desde la raíz del proyecto, con el .venv activo):
    python src/extract_vendor_attributes.py
"""
from pathlib import Path

import pandas as pd
from db import crear_conexion

RAIZ_PROYECTO = Path(__file__).resolve().parent.parent
CARPETA_DATOS = RAIZ_PROYECTO / "data" / "raw"

# LEFT JOIN: se conservan los 106 proveedores aunque alguno no tenga dirección registrada.
CONSULTA = """
    SELECT
        v.BusinessEntityID AS VendorID,
        v.AccountNumber,
        v.PurchasingWebServiceURL,
        bea.AddressTypeID,
        a.City,
        sp.Name AS Provincia,
        sp.CountryRegionCode,
        cr.Name AS Pais
    FROM Purchasing.Vendor AS v
    LEFT JOIN Person.BusinessEntityAddress AS bea ON bea.BusinessEntityID = v.BusinessEntityID
    LEFT JOIN Person.Address AS a ON a.AddressID = bea.AddressID
    LEFT JOIN Person.StateProvince AS sp ON sp.StateProvinceID = a.StateProvinceID
    LEFT JOIN Person.CountryRegion AS cr ON cr.CountryRegionCode = sp.CountryRegionCode
"""

engine = crear_conexion()

try:
    CARPETA_DATOS.mkdir(parents=True, exist_ok=True)
    df = pd.read_sql(CONSULTA, engine)

    ruta_csv = CARPETA_DATOS / "vendor_attributes.csv"
    df.to_csv(ruta_csv, index=False, encoding="utf-8-sig")

    print(f"Archivo guardado: {ruta_csv}")
    print(f"Filas: {df.shape[0]} | Proveedores únicos: {df['VendorID'].nunique()}")

    # Un proveedor puede tener más de una dirección: se revisa antes de usar los datos.
    repetidos = df['VendorID'].value_counts()
    print(f"Proveedores con más de una fila: {(repetidos > 1).sum()}")

    print("\nNulos por columna:")
    print(df.isnull().sum())
    print("\nProveedores por país:")
    print(df.drop_duplicates('VendorID')['Pais'].value_counts(dropna=False))
finally:
    engine.dispose()
