# 🚀 Manual de Instalación y Ejecución

Este manual detalla paso a paso cómo preparar, configurar y ejecutar el **Pipeline ETL y el Dashboard Web** desde cero.

---

## 🛠️ 1. Requisitos Previos

Asegúrate de tener instalado lo siguiente:
1. **Python 3.8 o superior** (Con "Add Python to PATH" marcado).
2. **MySQL Server** (XAMPP, WAMP, Workbench, etc.).
3. **Microsoft SQL Server** (Developer o Express).
4. **ODBC Driver for SQL Server** (Módulo para que Python hable con SQL Server).

---

## 🗄️ 2. Preparación de Bases de Datos

### Paso A: Base de Datos Origen (MySQL)
1. Abre tu gestor de MySQL.
2. Crea una base de datos vacía llamada `ccole` (o `bd_colegio` según tu preferencia).

### Paso B: Base de Datos Destino (SQL Server)
1. Abre SQL Server Management Studio (SSMS).
2. Abre y ejecuta el script **`Datamart_colegio.sql`**. 
3. Se creará la base de datos `datamart_colegio` con su Modelo en Estrella y vistas.

---

## 🐍 3. Instalación de Dependencias

Abre una **Terminal** en la carpeta del proyecto y ejecuta:

```powershell
pip install pandas numpy sqlalchemy pymysql pyodbc fastapi uvicorn
```

---

## ⚙️ 4. Configuración de Credenciales

Debes ajustar las credenciales de conexión en los archivos de Python (`generador_colegio.py` y `api.py` o `ETL_colegio.py`).

Busca las variables de entorno de conexión y colócalas así (ajusta si tienes contraseña):

```python
# Configuración para MySQL
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '', # Deja en blanco si no tienes clave, o pon la tuya
    'database': 'ccole'
}

# Configuración para SQL Server
SQLSERVER_CONFIG = 'mssql+pyodbc://localhost/datamart_colegio?driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes'
```

---

## 🎲 5. Generar Datos Transaccionales (OLTP)

Para que el Dashboard tenga algo que mostrar, primero inyectaremos miles de registros simulados a MySQL. En tu terminal ejecuta:

```powershell
python generador_colegio.py
```
*Espera a que el proceso termine e indique "PROCESO COMPLETADO EXITOSAMENTE".*

---

## 🌐 6. Ejecución del Dashboard Web y ETL

Una vez tengas datos en MySQL, levantaremos la página web:

1. En la terminal ejecuta:
```powershell
python -m uvicorn api:app --reload
```
2. Abre tu navegador y entra a: **👉 `http://127.0.0.1:8000`**

### ¿Cómo correr el ETL?
En la interfaz web, dirígete al menú izquierdo **"Data Pipeline (ETL)"** y presiona el botón **"Ejecutar Proceso ETL"**. 
Verás la consola en vivo extraendo datos de MySQL y cargándolos en SQL Server. Al finalizar, ve a la pestaña **"Visión General"** (presiona F5 si es necesario) para ver todas tus gráficas y KPIs actualizados.
