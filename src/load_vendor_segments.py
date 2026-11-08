"""Carga los segmentos de proveedores (K-Means) en la tabla bi.VendorSegmento.

Lee los archivos que generan los notebooks de Molina:
    - data/processed/purchasing_segmentacion_final.csv   (88 proveedores)
    - data/processed/prediccion_18_proveedores.csv       (opcional, 18 estimados)

Uso (desde la raíz del proyecto, con el .venv activo):
    python src/load_vendor_segments.py

La tabla bi.VendorSegmento la crea sql/01_modelo_estrella.sql. Este script solo
la vuelve a llenar; no la borra ni cambia su estructura.
"""
from pathlib import Path

import pandas as pd
from sqlalchemy import text

from db import crear_conexion

RAIZ_PROYECTO = Path(__file__).resolve().parent.parent
CARPETA_PROCESSED = RAIZ_PROYECTO / "data" / "processed"

# Proveedores de prueba que nunca deben entrar al modelo.
VENDEDORES_EXCLUIDOS = {1699, 1700}

COLUMNAS_SALIDA = ["VendorID", "Segmento", "EsEstimado"]


def _leer_csv(ruta: Path) -> pd.DataFrame:
    if not ruta.exists():
        raise FileNotFoundError(
            f"No se encontró {ruta}. "
            "Ejecuta primero los notebooks de segmentación de Molina."
        )
    return pd.read_csv(ruta, encoding="utf-8-sig")


def construir_tabla() -> pd.DataFrame:
    """Combina la segmentación real y, si existe, la predicción de los 18."""
    real = _leer_csv(CARPETA_PROCESSED / "purchasing_segmentacion_final.csv")

    if "VendorID" not in real.columns or "Segmento" not in real.columns:
        raise ValueError(
            "purchasing_segmentacion_final.csv debe tener las columnas "
            "VendorID y Segmento."
        )

    real = real[["VendorID", "Segmento"]].copy()
    real["EsEstimado"] = 0

    ruta_pred = CARPETA_PROCESSED / "prediccion_18_proveedores.csv"
    if ruta_pred.exists():
        pred = _leer_csv(ruta_pred)
        if "segmento_estimado" in pred.columns:
            pred = pred.rename(columns={"segmento_estimado": "Segmento"})
        if "VendorID" not in pred.columns or "Segmento" not in pred.columns:
            raise ValueError(
                "prediccion_18_proveedores.csv debe tener VendorID y "
                "segmento_estimado (o Segmento)."
            )
        pred = pred[["VendorID", "Segmento"]].copy()
        pred["EsEstimado"] = 1
        datos = pd.concat([real, pred], ignore_index=True)
    else:
        datos = real

    datos["VendorID"] = pd.to_numeric(datos["VendorID"], errors="coerce")
    datos = datos.dropna(subset=["VendorID", "Segmento"])
    datos["VendorID"] = datos["VendorID"].astype(int)
    datos["Segmento"] = datos["Segmento"].astype(str).str.strip()
    datos["EsEstimado"] = datos["EsEstimado"].astype(int)

    # Si un proveedor aparece en ambos archivos, se conserva el segmento real.
    datos = (
        datos.sort_values("EsEstimado")
        .drop_duplicates("VendorID", keep="first")
        .reset_index(drop=True)
    )

    # Nunca cargar los proveedores de prueba.
    datos = datos[~datos["VendorID"].isin(VENDEDORES_EXCLUIDOS)]

    return datos[COLUMNAS_SALIDA]


def cargar_segmentos() -> None:
    datos = construir_tabla()

    engine = crear_conexion()
    try:
        with engine.begin() as conexion:
            conexion.execute(text("DELETE FROM bi.VendorSegmento"))
            datos.to_sql(
                "VendorSegmento",
                conexion,
                schema="bi",
                if_exists="append",
                index=False,
            )

        print("\nSegmentos cargados en bi.VendorSegmento.")
        print(f"Proveedores cargados: {len(datos)}")
        print("\nDistribución:")
        print(datos["Segmento"].value_counts().to_string())
        print("\nEstimados:", int(datos["EsEstimado"].sum()))
    finally:
        engine.dispose()


if __name__ == "__main__":
    cargar_segmentos()
