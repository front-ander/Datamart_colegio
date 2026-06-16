# 🚀 Manual de Instalación y Ejecución (Módulo Web ETL)

Este manual detalla paso a paso cómo preparar, configurar y ejecutar el **Data Mart Pipeline (ETL y Dashboard Web)** desde cero en cualquier computadora nueva.

---

## 🛠️ 1. Requisitos Previos (Software Necesario)

Asegúrate de que la nueva computadora tenga instalado lo siguiente:

1. **Python 3.8 o superior** (No olvides marcar la casilla *"Add Python to PATH"* durante la instalación).
2. **MySQL Server** (Puede ser XAMPP, WAMP, o MySQL directo) para la base de datos de origen.
3. **Microsoft SQL Server** (Developer o Express edition) para el Data Mart de destino.
4. **ODBC Driver for SQL Server**: Generalmente viene con SQL Server, pero si la conexión falla, asegúrate de tener instalado el [ODBC Driver 17 for SQL Server](https://learn.microsoft.com/es-es/sql/connect/odbc/download-odbc-driver-for-sql-server).

---

## 🗄️ 2. Preparación de las Bases de Datos

Antes de correr el código, las bases de datos deben existir en los motores correspondientes.

### Paso A: Base de Datos Origen (MySQL)
1. Abre tu gestor de MySQL (ej. phpMyAdmin, DBeaver, MySQL Workbench).
2. Crea una base de datos vacía llamada `bd_colegio`.
3. Importa el archivo **`ccole (2).sql`** que viene en el proyecto. Esto creará todas las tablas OLTP (personas, estudiantes, notas, etc.) y las poblará con miles de datos de prueba.

### Paso B: Base de Datos Destino (SQL Server)
1. Abre SQL Server Management Studio (SSMS).
2. Abre y ejecuta el archivo **`Datamart_colegio.sql`**. 
3. *Nota: Este script creará automáticamente la base de datos `datamart_colegio`, el esquema de estrella (Tablas Dimensión y Hechos) y las vistas analíticas.*

---

## 🐍 3. Instalación de Dependencias Python

Abre una **Terminal** (PowerShell o CMD) en la carpeta del proyecto y ejecuta el siguiente comando para instalar todas las librerías necesarias:

```powershell
pip install pandas numpy sqlalchemy pymysql pyodbc fastapi uvicorn
```

*¿Qué instala esto?*
* `pandas` / `numpy`: Para la manipulación y transformación de datos en memoria.
* `sqlalchemy` / `pymysql` / `pyodbc`: Drivers para conectarse a MySQL y SQL Server.
* `fastapi` / `uvicorn`: Framework para levantar el servidor y el Dashboard Web en tiempo real.

---

## ⚙️ 4. Configuración de Credenciales

Abre el archivo **`ETL_colegio.py`** con cualquier editor de texto o código y busca la sección de configuración (alrededor de la línea 15).

Ajusta las credenciales según la computadora nueva:

**Para MySQL:**
```python
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root', # Tu usuario de MySQL
    'password': 'tu_contraseña_aqui', # <-- PON LA CONTRASEÑA CORRECTA
    'database': 'bd_colegio'
}
```

**Para SQL Server:**
Generalmente, si usas Windows Authentication, esta cadena genérica funciona conectándose al `localhost`:
```python
SQLSERVER_CONFIG = 'mssql+pyodbc://localhost/Datamart_colegio?driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes'
```
*(Si SQL Server tiene un nombre de instancia específico, cambia `localhost` por `NombreDeTuPC\SQLEXPRESS`).*

---

## 🌐 5. Ejecución del Dashboard Web

Con las bases de datos listas y las librerías instaladas, levantar el sistema es muy sencillo:

1. Abre la terminal en la carpeta del proyecto.
2. Ejecuta el servidor web con el siguiente comando:

```powershell
python -m uvicorn api:app --reload
```

3. Espera a ver el mensaje `Application startup complete`.
4. Abre tu navegador web (Chrome, Edge, Firefox) y entra a:
   **👉 `http://127.0.0.1:8000`**

---

## 📊 6. Uso del Sistema

1. Al entrar a la web, verás el **Data Mart Pipeline** con todos los nodos en estado *Pendiente*.
2. Haz clic en el botón azul **"Ejecutar ETL"** en la esquina superior derecha.
3. Observa la magia: Los bloques empezarán a procesarse secuencialmente, cambiando a azul (procesando) y luego a verde (completado), mostrando el conteo de filas insertadas en SQL Server exactamente igual que en herramientas profesionales como SSIS.
4. El registro (log) inferior te mostrará el detalle técnico y los tiempos de ejecución.
