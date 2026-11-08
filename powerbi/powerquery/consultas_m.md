# Consultas Power Query (M) — vistas del esquema `bi`

Estas consultas son opcionales: al conectar Power BI Desktop con **Azure SQL Database**, el Navegador ya muestra las vistas del esquema `bi` y se pueden cargar con un clic.

Se incluyen para dejar reproducible la conexión y para el caso de que se prefiera crear cada consulta manualmente con **Transformar datos → Editor avanzado**.

---

## 1. Crear los parámetros

En Power Query: **Inicio → Administrar parámetros → Nuevo parámetro**.

| Nombre | Tipo | Valor sugerido |
|---|---|---|
| `Servidor` | Texto | `sebastian-sql-server-2026.database.windows.net` |
| `BaseDatos` | Texto | `AdventureWorks2` |

---

## 2. Consultas

### `DimProveedor`

```m
let
    Origen = Sql.Database(Servidor, BaseDatos),
    Vista  = Origen{[Schema = "bi", Item = "DimProveedor"]}[Data]
in
    Vista
```

### `DimProducto`

```m
let
    Origen = Sql.Database(Servidor, BaseDatos),
    Vista  = Origen{[Schema = "bi", Item = "DimProducto"]}[Data]
in
    Vista
```

### `DimFecha`

```m
let
    Origen = Sql.Database(Servidor, BaseDatos),
    Vista  = Origen{[Schema = "bi", Item = "DimFecha"]}[Data]
in
    Vista
```

### `DimMetodoEnvio`

```m
let
    Origen = Sql.Database(Servidor, BaseDatos),
    Vista  = Origen{[Schema = "bi", Item = "DimMetodoEnvio"]}[Data]
in
    Vista
```

### `DimEstadoOrden`

```m
let
    Origen = Sql.Database(Servidor, BaseDatos),
    Vista  = Origen{[Schema = "bi", Item = "DimEstadoOrden"]}[Data]
in
    Vista
```

### `FactCompras`

```m
let
    Origen = Sql.Database(Servidor, BaseDatos),
    Vista  = Origen{[Schema = "bi", Item = "FactCompras"]}[Data]
in
    Vista
```

### `FactOrdenes`

```m
let
    Origen = Sql.Database(Servidor, BaseDatos),
    Vista  = Origen{[Schema = "bi", Item = "FactOrdenes"]}[Data]
in
    Vista
```

---

## 3. Notas

- Las vistas ya aplican la exclusión de los proveedores **1699** y **1700**. No hace falta volver a filtrar en Power Query.
- No cambiar los nombres de las consultas: las medidas DAX y las relaciones usan esos nombres.
- Si se agrega una columna nueva a una vista, actualizar la consulta y volver a cargar.
- Las credenciales se ingresan en Power BI al conectar; no se escriben en el código M.
