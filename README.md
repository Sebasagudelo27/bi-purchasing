# BI Purchasing – Sprint 1

## Descripción

Proyecto de análisis de datos del esquema Purchasing de AdventureWorks2025. El objetivo es extraer, preparar y explorar información de compras y proveedores para apoyar el análisis de datos y la posterior segmentación de proveedores mediante K-Means.

## Objetivos del Sprint 1

- Configurar la conexión con la base de datos.
- Extraer las tablas necesarias del esquema Purchasing.
- Inspeccionar la estructura y calidad de los datos.
- Consolidar información relevante por proveedor.
- Preparar la documentación y el entorno para el análisis exploratorio y la segmentación.

## Estructura del proyecto

```text
bi-purchasing/
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
├── src/
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

## Tecnologías

- Python
- SQL Server
- SQLAlchemy y pyodbc
- Pandas y NumPy
- Jupyter Notebook
- Matplotlib y Seaborn
- Scikit-learn

## Configuración

1. Clonar el repositorio.
2. Crear un entorno virtual de Python.
3. Instalar las dependencias con `pip install -r requirements.txt`.
4. Configurar las variables de conexión en un archivo `.env`, tomando como referencia `.env.example`.
5. Ejecutar el script de extracción ubicado en `src/` para obtener los datos.

**Importante:** no subir el archivo `.env` ni publicar contraseñas, credenciales o datos sensibles.

## Datos

Los archivos CSV extraídos se almacenan localmente en `data/raw/`. Los resultados consolidados se guardan en `data/processed/`. Ambas carpetas están excluidas de Git para evitar publicar información sin revisar.

## Estado del proyecto

- [x] Configuración inicial del repositorio.
- [x] Conexión con la base de datos.
- [x] Extracción de tablas.
- [x] Inspección inicial de los datos.
- [x] Consolidación básica por proveedor.
- [x] Documentación inicial del proyecto.
- [ ] Análisis exploratorio de datos (EDA).
- [ ] Segmentación de proveedores mediante K-Means.
- [ ] Integración de resultados y conclusiones del sprint.

## Configuración del entorno y extracción de datos

### 1. Requisitos previos

- Tener Python instalado.
- Tener Git instalado.
- Tener instalado el controlador ODBC 18 para SQL Server.
- Contar con acceso autorizado a la base de datos Azure SQL Database AdventureWorks2025.

### 2. Descargar el proyecto

Clonar el repositorio y entrar en su carpeta:

```bash
git clone URL_DEL_REPOSITORIO
cd bi-purchasing
```

### 3. Crear y activar el entorno virtual

En Windows, desde Git Bash:

```bash
python -m venv .venv
source .venv/Scripts/activate
```

### 4. Instalar las dependencias

```bash
python -m pip install -r requirements.txt
```

### 5. Configurar la conexión a Azure

Crear un archivo `.env` tomando como referencia `.env.example`.

Completar las variables con las credenciales propias autorizadas para acceder a Azure SQL Database. No subir el archivo `.env` a GitHub ni compartir contraseñas por el repositorio.

### 6. Extraer los datos

Ejecutar el script de extracción desde la raíz del proyecto:

```bash
python src/extract_data.py
```

Los archivos CSV se guardarán localmente en `data/raw/`.

### 7. Consolidar los datos

Una vez extraídos los CSV, ejecutar:

```bash
python src/consolidate_data.py
```

El archivo consolidado se generará en `data/processed/`.

### 8. Trabajar con los datos

Cada integrante puede utilizar los CSV locales para desarrollar su parte del proyecto. No es necesario conectarse a Azure cada vez que se realiza un análisis.

**Importante:** cada integrante necesita permisos de acceso a la base de datos. Si no tiene acceso, debe solicitarlo al responsable del proyecto antes de ejecutar la extracción.
