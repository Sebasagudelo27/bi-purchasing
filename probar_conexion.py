from src.db import crear_conexion

engine = crear_conexion()
engine.dispose()