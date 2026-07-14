# 🚀 Manual de Instalación y Despliegue - Dashboard BI Colegio

Este manual detalla paso a paso cómo preparar, configurar y ejecutar el **Pipeline ETL, la Base de Datos y el Dashboard Web** en una computadora nueva desde cero.

---

## 🛠️ 1. Requisitos Previos (Instalación)

Asegúrate de tener instalados los siguientes programas en la nueva computadora:
1. **Python 3.8 o superior** (Durante la instalación, asegúrate de marcar la casilla *"Add Python to PATH"*).
2. **Node.js y npm** (Para compilar el frontend en React).
3. **MySQL Server** (Puede ser a través de XAMPP, WAMP o MySQL Workbench) para la base de datos de origen.
4. **Microsoft SQL Server** (Developer o Express) para la base de datos destino (Datamart).
5. **ODBC Driver for SQL Server** (Necesario para que Python se comunique con SQL Server).

---

## 🗄️ 2. Preparación de Bases de Datos

### Base de Datos Origen (MySQL)
1. Abre tu gestor de MySQL (ej. phpMyAdmin o Workbench).
2. Crea una base de datos llamada `ccole` (o importa tu script de datos actual `ccole (2).sql` si lo tienes para restaurar los datos transaccionales de origen).
3. Si la base de datos está vacía, ejecuta el archivo `generador_colegio.py` para llenarla con datos simulados:
   ```bash
   python generador_colegio.py
   ```

### Base de Datos Destino (SQL Server)
1. Abre SQL Server Management Studio (SSMS).
2. Abre y ejecuta el script **`Datamart_colegio.sql`**. 
3. Se creará automáticamente la base de datos `Datamart_colegio` con su Modelo en Estrella (tablas de dimensiones y hechos).

---

## ⚙️ 3. Configuración de Credenciales

Abre el archivo `ETL_colegio.py` y verifica que las credenciales coincidan con tu nueva computadora:

```python
# Configuración para MySQL
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '', # Coloca la contraseña de MySQL de la nueva PC
    'database': 'ccole'
}

# Configuración para SQL Server
SQLSERVER_CONFIG = 'mssql+pyodbc://localhost/Datamart_colegio?driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes'
```
*(Haz lo mismo en `api.py` si tiene configuraciones directas).*

---

## 📦 4. Instalación de Dependencias (Python y Node)

### Dependencias del Backend (Python)
Abre una terminal en la carpeta principal del proyecto (Datamart) e instala las librerías necesarias:
```bash
pip install pandas numpy sqlalchemy pymysql pyodbc fastapi uvicorn
```

### Dependencias del Frontend (React)
Abre una terminal y navega hasta la carpeta del frontend:
```bash
cd dashboard-colegio
npm install
```

---

## 🔄 5. Compilar el Frontend y Ejecutar el ETL

### Paso A: Compilar la Página Web
Para que el servidor de Python pueda mostrar la web, debes compilar React. Desde la carpeta `dashboard-colegio`, ejecuta:
```bash
npm run build
```
*(Gracias a la configuración en `vite.config.js`, esto automáticamente colocará los archivos finales en la carpeta `public/` de la raíz).*

### Paso B: Ejecutar el ETL
Abre una terminal en la raíz del proyecto (Datamart) y ejecuta el proceso ETL para migrar la información de MySQL a SQL Server:
```bash
python ETL_colegio.py
```
*(Espera a que el proceso indique que finalizó la carga de los Hechos).*

---

## 🌐 6. Levantar el Sistema y Ver el Dashboard

1. En la consola (ubicado en la raíz del proyecto `Datamart`), levanta el servidor backend con FastAPI:
   ```bash
   python -m uvicorn api:app --reload
   ```
2. Abre tu navegador web favorito (Chrome, Edge, etc.).
3. Ingresa a la URL local: **👉 `http://127.0.0.1:8000`**

¡Listo! Tu sistema y dashboard estarán operando completamente en la nueva computadora. Si más adelante haces cambios en el código de React, solo recuerda volver a ejecutar `npm run build` en su respectiva carpeta.
