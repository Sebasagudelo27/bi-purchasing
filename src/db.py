import os
import pyodbc
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

load_dotenv()
def crear_conexion():
    parametros = {
        "server": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
        "database": os.getenv("DB_NAME"),
        "username": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
    }
    faltantes = [
        nombre
        for nombre, valor in parametros.items()
        if not valor
    ]

    if faltantes:
        raise ValueError(
            f"Faltan variables en el archivo .env: {faltantes}"
        )
        
    driver = "ODBC Driver 18 for SQL Server"
    if driver not in pyodbc.drivers():
        raise RuntimeError(f"No está instalado: {driver}")
    
    url = URL.create(
         "mssql+pyodbc",
        username=parametros["username"],
        password=parametros["password"],
        host=parametros["server"],
        port=int(parametros["port"]),
        database=parametros["database"],
        query={
            "driver": driver,
            "Encrypt": "yes",
            "TrustServerCertificate": "no",
        },
    )
    
    engine = create_engine(url, pool_pre_ping=True)
    
    try:
        with engine.connect() as conexion:
            base = conexion.execute(
                text("SELECT DB_NAME()")
            ).scalar_one()

            print("Conexión exitosa.")
            print(f"Base de datos: {base}")

        return engine
    except Exception as e:
        print("Error al conectar a la base de datos:", e)
        raise