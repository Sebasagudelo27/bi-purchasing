
from pathlib import Path
import pandas as pd

RAIZ_PROYECTO = Path(__file__).resolve().parent.parent
CARPETA_DATOS = RAIZ_PROYECTO / "data" / "raw"

tablas = [
    "vendor",
    "purchase_order_header",
    "purchase_order_detail",
    "product_vendor",
    "ship_method",
    "product",
]

for nombre in tablas:
    ruta = CARPETA_DATOS / f"{nombre}.csv"
    df = pd.read_csv(ruta)

    print(f"\n{'=' * 50}")
    print(f"TABLA: {nombre}")
    print(f"Filas y columnas: {df.shape}")

    print("\nColumnas:")
    print(df.columns.tolist())

    print("\nValores nulos por columna:")
    print(df.isnull().sum())

    print("\nPrimeras 3 filas:")
    print(df.head(3))

