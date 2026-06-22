from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from ETL_colegio import ejecutar_etl, SQLSERVER_CONFIG, connect_with_retry
import os
import pandas as pd
from sqlalchemy import text

app = FastAPI()

# Configurar CORS por si fuera necesario
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    """Obtiene una conexión resiliente a SQL Server para el Dashboard"""
    try:
        engine = connect_with_retry(SQLSERVER_CONFIG, max_retries=2, delay=2)
        return engine
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")

@app.get("/api/kpis")
def get_kpis():
    engine = get_db_connection()
    try:
        with engine.connect() as conn:
            # Total estudiantes
            total_estudiantes = conn.execute(text("SELECT COUNT(DISTINCT id_estudiante_sk) FROM HechoRendimientoAcademico")).scalar() or 0
            # Promedio general
            promedio_general = conn.execute(text("SELECT AVG(nota_obtenida) FROM HechoRendimientoAcademico")).scalar() or 0
            # Total cursos
            total_cursos = conn.execute(text("SELECT COUNT(DISTINCT id_curso_sk) FROM HechoRendimientoAcademico")).scalar() or 0
            # Total asistencias / total registros
            asistencias_query = conn.execute(text("""
                SELECT SUM(asistencias) FROM (
                    SELECT id_estudiante_sk, MAX(cantidad_asistencias) as asistencias 
                    FROM HechoRendimientoAcademico 
                    GROUP BY id_estudiante_sk
                ) t
            """)).scalar() or 0
            
            return {
                "total_estudiantes": total_estudiantes,
                "promedio_general": round(float(promedio_general), 2),
                "total_cursos": total_cursos,
                "total_asistencias": int(asistencias_query)
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chart/grades")
def get_chart_grades():
    engine = get_db_connection()
    try:
        query = """
        SELECT c.nombre_curso, AVG(h.nota_obtenida) as promedio
        FROM HechoRendimientoAcademico h
        JOIN DimCurso c ON h.id_curso_sk = c.id_curso_sk
        GROUP BY c.nombre_curso
        ORDER BY promedio DESC
        """
        df = pd.read_sql(query, engine)
        return {
            "labels": df['nombre_curso'].tolist(),
            "data": [round(float(x), 2) for x in df['promedio'].tolist()]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chart/attendance")
def get_chart_attendance():
    engine = get_db_connection()
    try:
        query = """
        SELECT g.grado, SUM(t.asistencias) as asistencias, SUM(t.ausencias) as ausencias
        FROM (
            SELECT h.id_estudiante_sk, h.id_grado_seccion_sk, MAX(h.cantidad_asistencias) as asistencias, MAX(h.cantidad_ausencias) as ausencias
            FROM HechoRendimientoAcademico h
            GROUP BY h.id_estudiante_sk, h.id_grado_seccion_sk
        ) t
        JOIN DimGradoSeccion g ON t.id_grado_seccion_sk = g.id_grado_seccion_sk
        GROUP BY g.grado
        """
        df = pd.read_sql(query, engine)
        return {
            "labels": df['grado'].tolist(),
            "asistencias": [int(x) for x in df['asistencias'].tolist()],
            "ausencias": [int(x) for x in df['ausencias'].tolist()]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/table/recent")
def get_table_recent():
    engine = get_db_connection()
    try:
        query = "SELECT TOP 50 Estudiante, Grado, Curso, Profesor, Nota, Estado FROM vw_RendimientoAcademico ORDER BY NEWID()"
        df = pd.read_sql(query, engine)
        # Convertir a float las notas para JSON
        df['Nota'] = df['Nota'].astype(float).round(2)
        return df.to_dict(orient="records")
    except Exception as e:
        # Si la vista no existe, devolvemos un arreglo vacio amigablemente
        return []

@app.get("/api/run-etl")
def run_etl_endpoint():
    """
    Ejecuta el ETL y transmite los eventos en tiempo real al frontend
    usando Server-Sent Events (SSE).
    """
    def event_stream():
        for log in ejecutar_etl():
            yield f"data: {log}\n\n"
            
    return StreamingResponse(event_stream(), media_type="text/event-stream")

# Crear el directorio public si no existe
os.makedirs("public", exist_ok=True)

# Montar los archivos estáticos del frontend (HTML, CSS, JS)
app.mount("/", StaticFiles(directory="public", html=True), name="public")

if __name__ == "__main__":
    print("Iniciando servidor web de Dashboard BI en http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
