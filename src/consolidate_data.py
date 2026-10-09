
from pathlib import Path

import pandas as pd


# Rutas del proyecto
RAIZ_PROYECTO = Path(__file__).resolve().parent.parent
CARPETA_RAW = RAIZ_PROYECTO / "data" / "raw"
CARPETA_PROCESSED = RAIZ_PROYECTO / "data" / "processed"


def cargar_csv(nombre):
    ruta = CARPETA_RAW / f"{nombre}.csv"
    return pd.read_csv(ruta)


def consolidar_datos():
    # 1. Cargar las tablas
    vendor = cargar_csv("vendor")
    header = cargar_csv("purchase_order_header")
    detail = cargar_csv("purchase_order_detail")
    product_vendor = cargar_csv("product_vendor")
    product = cargar_csv("product")
    ship_method = cargar_csv("ship_method")

    print("Tablas cargadas correctamente.")

    # 2. Resumir las órdenes por proveedor
    resumen_ordenes = (
        header.groupby("VendorID")
        .agg(
            NumeroOrdenes=("PurchaseOrderID", "nunique"),
            ValorTotalOrdenes=("TotalDue", "sum"),
            GastoPromedioOrden=("TotalDue", "mean"),
            UltimaOrden=("OrderDate", "max"),
        )
        .reset_index()
    )

    # 3. Relacionar el detalle con la cabecera
    # Aquí NO sumamos TotalDue; usamos datos propios del detalle.
    detalle_con_orden = detail.merge(
        header[["PurchaseOrderID", "VendorID"]],
        on="PurchaseOrderID",
        how="inner",
        validate="many_to_one",
    )

    resumen_detalle = (
        detalle_con_orden.groupby("VendorID")
        .agg(
            UnidadesPedidas=("OrderQty", "sum"),
            ProductosComprados=("ProductID", "nunique"),
            ValorLineas=("LineTotal", "sum"),
        )
        .reset_index()
    )

    # 4. Resumir el catálogo de productos por proveedor
    # ProductVendor relaciona BusinessEntityID con ProductID.
    productos_con_info = product_vendor.merge(
        product[["ProductID", "Name", "StandardCost", "ListPrice"]],
        on="ProductID",
        how="left",
        validate="many_to_one",
        suffixes=("_Proveedor", "_Producto"),
    )

    resumen_productos = (
        productos_con_info.groupby("BusinessEntityID")
        .agg(
            ProductosOfrecidos=("ProductID", "nunique"),
            TiempoEntregaPromedio=("AverageLeadTime", "mean"),
            PrecioEstandarPromedio=("StandardPrice", "mean"),
        )
        .reset_index()
        .rename(columns={"BusinessEntityID": "VendorID"})
    )

    # 5. Unir los resúmenes a la tabla de proveedores
    consolidado = vendor[
        [
            "BusinessEntityID",
            "Name",
            "CreditRating",
            "PreferredVendorStatus",
            "ActiveFlag",
        ]
    ].rename(
        columns={
            "BusinessEntityID": "VendorID",
            "Name": "NombreProveedor",
        }
    )

    consolidado = consolidado.merge(
        resumen_ordenes,
        on="VendorID",
        how="left",
        validate="one_to_one",
    )

    consolidado = consolidado.merge(
        resumen_detalle,
        on="VendorID",
        how="left",
        validate="one_to_one",
    )

    consolidado = consolidado.merge(
        resumen_productos,
        on="VendorID",
        how="left",
        validate="one_to_one",
    )

    # 6. Revisar los resultados antes de guardar
    CARPETA_PROCESSED.mkdir(parents=True, exist_ok=True)

    ruta_salida = CARPETA_PROCESSED / "purchasing_consolidated.csv"
    consolidado.to_csv(ruta_salida, index=False, encoding="utf-8-sig")

    print("\nConsolidación terminada.")
    print(f"Proveedores: {len(consolidado)}")
    print(f"Columnas: {len(consolidado.columns)}")
    print(f"Archivo guardado en: {ruta_salida}")

    print("\nValores nulos por columna:")
    print(consolidado.isnull().sum())

    print("\nPrimeras filas:")
    print(consolidado.head())


if __name__ == "__main__":
    consolidar_datos()
    id="w8q1mt"
