from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from ETL_colegio import ejecutar_etl, SQLSERVER_CONFIG, connect_with_retry
import os
import pandas as pd
from sqlalchemy import text
from typing import Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    try:
        engine = connect_with_retry(SQLSERVER_CONFIG, max_retries=2, delay=2)
        return engine
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")

def build_where_clause(anio: Optional[int], grado: Optional[str], include_grado_join=True, alias_h="h", alias_t="t", alias_g="g"):
    conditions = []
    params = {}
    if anio:
        conditions.append(f"{alias_t}.anio = :anio")
        params["anio"] = anio
    if grado:
        conditions.append(f"{alias_g}.grado = :grado")
        params["grado"] = grado
        
    where_sql = ""
    join_sql = ""
    if grado and include_grado_join:
        join_sql = f" JOIN DimGradoSeccion {alias_g} ON {alias_h}.id_grado_seccion_sk = {alias_g}.id_grado_seccion_sk "
    
    if conditions:
        where_sql = " WHERE " + " AND ".join(conditions)
        
    return join_sql, where_sql, params

@app.get("/api/kpis")
def get_kpis(anio: int = Query(None), grado: str = Query(None)):
    engine = get_db_connection()
    try:
        join_sql, where_sql, params = build_where_clause(anio, grado)
        
        q_estudiantes = f"SELECT COUNT(DISTINCT h.id_estudiante_sk) FROM HechoRendimientoAcademico h JOIN DimTiempo t ON h.id_tiempo = t.id_tiempo {join_sql} {where_sql}"
        q_promedio = f"SELECT AVG(h.nota_obtenida) FROM HechoRendimientoAcademico h JOIN DimTiempo t ON h.id_tiempo = t.id_tiempo {join_sql} {where_sql}"
        q_cursos = f"SELECT COUNT(DISTINCT h.id_curso_sk) FROM HechoRendimientoAcademico h JOIN DimTiempo t ON h.id_tiempo = t.id_tiempo {join_sql} {where_sql}"
        
        q_asistencias = f"""
            SELECT SUM(asistencias) FROM (
                SELECT h.id_estudiante_sk, MAX(h.cantidad_asistencias) as asistencias 
                FROM HechoRendimientoAcademico h 
                JOIN DimTiempo t ON h.id_tiempo = t.id_tiempo
                {join_sql} {where_sql}
                GROUP BY h.id_estudiante_sk
            ) tmp
        """
        
        with engine.connect() as conn:
            total_estudiantes = conn.execute(text(q_estudiantes), params).scalar() or 0
            promedio_general = conn.execute(text(q_promedio), params).scalar() or 0
            total_cursos = conn.execute(text(q_cursos), params).scalar() or 0
            total_asistencias = conn.execute(text(q_asistencias), params).scalar() or 0
            
            return {
                "total_estudiantes": total_estudiantes,
                "promedio_general": round(float(promedio_general), 2),
                "total_cursos": total_cursos,
                "total_asistencias": int(total_asistencias)
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chart/grades")
def get_chart_grades(anio: int = Query(None), grado: str = Query(None)):
    engine = get_db_connection()
    try:
        join_sql, where_sql, params = build_where_clause(anio, grado)
        query = f"""
        SELECT c.nombre_curso, AVG(h.nota_obtenida) as promedio
        FROM HechoRendimientoAcademico h
        JOIN DimCurso c ON h.id_curso_sk = c.id_curso_sk
        JOIN DimTiempo t ON h.id_tiempo = t.id_tiempo
        {join_sql}
        {where_sql}
        GROUP BY c.nombre_curso
        ORDER BY promedio DESC
        """
        df = pd.read_sql(text(query), engine, params=params)
        return {
            "labels": df['nombre_curso'].tolist(),
            "data": [round(float(x), 2) for x in df['promedio'].tolist()]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chart/attendance")
def get_chart_attendance(anio: int = Query(None), grado: str = Query(None)):
    engine = get_db_connection()
    try:
        join_sql, where_sql, params = build_where_clause(anio, grado, include_grado_join=False)
        # Note: We group by grado, so we must join DimGradoSeccion anyway here
        # But we also want to filter by the requested grado if any
        if not grado:
            join_sql = " JOIN DimGradoSeccion g ON tmp.id_grado_seccion_sk = g.id_grado_seccion_sk "
        else:
            join_sql = " JOIN DimGradoSeccion g ON tmp.id_grado_seccion_sk = g.id_grado_seccion_sk "

        query = f"""
        SELECT g.grado, SUM(tmp.asistencias) as asistencias, SUM(tmp.ausencias) as ausencias
        FROM (
            SELECT h.id_estudiante_sk, h.id_grado_seccion_sk, MAX(h.cantidad_asistencias) as asistencias, MAX(h.cantidad_ausencias) as ausencias
            FROM HechoRendimientoAcademico h
            JOIN DimTiempo t ON h.id_tiempo = t.id_tiempo
            {where_sql.replace('g.grado', 'h.id_grado_seccion_sk = (SELECT TOP 1 id_grado_seccion_sk FROM DimGradoSeccion WHERE grado=:grado)') if grado else ''}
            GROUP BY h.id_estudiante_sk, h.id_grado_seccion_sk
        ) tmp
        JOIN DimGradoSeccion g ON tmp.id_grado_seccion_sk = g.id_grado_seccion_sk
        GROUP BY g.grado
        """
        # A simpler way for attendance:
        
        params2 = {}
        where2 = ""
        if anio: params2["anio"] = anio; where2 += " AND t.anio = :anio"
        if grado: params2["grado"] = grado; where2 += " AND g.grado = :grado"

        simpler_query = f"""
        SELECT g.grado, SUM(tmp.asistencias) as asistencias, SUM(tmp.ausencias) as ausencias
        FROM (
            SELECT h.id_estudiante_sk, h.id_grado_seccion_sk, MAX(h.cantidad_asistencias) as asistencias, MAX(h.cantidad_ausencias) as ausencias
            FROM HechoRendimientoAcademico h
            JOIN DimTiempo t ON h.id_tiempo = t.id_tiempo
            JOIN DimGradoSeccion g ON h.id_grado_seccion_sk = g.id_grado_seccion_sk
            WHERE 1=1 {where2}
            GROUP BY h.id_estudiante_sk, h.id_grado_seccion_sk, g.grado
        ) tmp
        JOIN DimGradoSeccion g ON tmp.id_grado_seccion_sk = g.id_grado_seccion_sk
        GROUP BY g.grado
        """
        df = pd.read_sql(text(simpler_query), engine, params=params2)
        return {
            "labels": df['grado'].tolist(),
            "asistencias": [int(x) for x in df['asistencias'].tolist()],
            "ausencias": [int(x) for x in df['ausencias'].tolist()]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/rendimiento")
def get_rendimiento(anio: int = Query(None), grado: str = Query(None)):
    engine = get_db_connection()
    try:
        join_sql, where_sql, params = build_where_clause(anio, grado)
        query = f"""
        SELECT 
            t.anio AS Año,
            COUNT(DISTINCT h.id_estudiante_sk) AS total,
            SUM(CASE WHEN h.nota_obtenida >= 11 THEN 1 ELSE 0 END) AS aprobados,
            SUM(CASE WHEN h.nota_obtenida < 11 THEN 1 ELSE 0 END) AS desaprobados
        FROM HechoRendimientoAcademico h
        JOIN DimTiempo t ON h.id_tiempo = t.id_tiempo
        {join_sql}
        {where_sql}
        GROUP BY t.anio ORDER BY t.anio DESC
        """
        df = pd.read_sql(text(query), engine, params=params)
        return df.to_dict(orient="records")
    except Exception as e:
        return []

@app.get("/api/asistencia-detallada")
def get_asistencia_detallada(anio: int = Query(None), grado: str = Query(None)):
    engine = get_db_connection()
    try:
        join_sql, where_sql, params = build_where_clause(anio, grado)
        query = f"""
        SELECT 
            tmp.anio AS Año,
            SUM(tmp.ausencias) AS ausencias,
            SUM(tmp.asistencias) AS asistencias,
            SUM(tmp.tardanzas) AS tardanzas
        FROM (
            SELECT h.id_estudiante_sk, t.anio, 
                   MAX(h.cantidad_ausencias) as ausencias, 
                   MAX(h.cantidad_asistencias) as asistencias, 
                   MAX(h.cantidad_tardanzas) as tardanzas
            FROM HechoRendimientoAcademico h
            JOIN DimTiempo t ON h.id_tiempo = t.id_tiempo
            {join_sql}
            {where_sql}
            GROUP BY h.id_estudiante_sk, t.anio
        ) tmp
        GROUP BY tmp.anio ORDER BY tmp.anio DESC
        """
        df = pd.read_sql(text(query), engine, params=params)
        return df.to_dict(orient="records")
    except Exception as e:
        return []

@app.get("/api/riesgo")
def get_riesgo(anio: int = Query(None), grado: str = Query(None)):
    engine = get_db_connection()
    try:
        join_sql, where_sql, params = build_where_clause(anio, grado)
        query = f"""
        SELECT TOP 10
            e.nombre_completo AS estudiante,
            e.grado_academico AS grado,
            t.anio AS Año,
            ROUND(AVG(h.nota_obtenida), 2) AS promedio_notas,
            MAX(h.cantidad_ausencias) AS total_Ausencias,
            ROUND(
                (1 - AVG(h.nota_obtenida) / 20) * 40 + 
                (MAX(h.cantidad_ausencias) / 20) * 30, 2
            ) AS indice_riesgo
        FROM HechoRendimientoAcademico h
        JOIN DimEstudiante e ON h.id_estudiante_sk = e.id_estudiante_sk
        JOIN DimTiempo t ON h.id_tiempo = t.id_tiempo
        {join_sql}
        {where_sql}
        GROUP BY e.id_estudiante_sk, e.nombre_completo, e.grado_academico, t.anio
        ORDER BY Indice_Riesgo DESC
        """
        df = pd.read_sql(text(query), engine, params=params)
        return df.to_dict(orient="records")
    except Exception as e:
        return []

@app.get("/api/docentes")
def get_docentes(anio: int = Query(None), grado: str = Query(None)):
    engine = get_db_connection()
    try:
        join_sql, where_sql, params = build_where_clause(anio, grado)
        query = f"""
        SELECT 
            p.nombre_completo AS profesor,
            p.especialidad AS especialidad,
            COUNT(*) AS total_Notas,
            ROUND(AVG(h.nota_obtenida), 2) AS promedio,
            ROUND(STDEV(h.nota_obtenida), 2) AS desviacion
        FROM HechoRendimientoAcademico h
        JOIN DimProfesor p ON h.id_profesor_sk = p.id_profesor_sk
        JOIN DimTiempo t ON h.id_tiempo = t.id_tiempo
        {join_sql}
        {where_sql}
        GROUP BY p.nombre_completo, p.especialidad
        HAVING COUNT(*) >= 10
        ORDER BY Promedio DESC
        """
        df = pd.read_sql(text(query), engine, params=params)
        df['desviacion'] = df['desviacion'].fillna(0)
        return df.to_dict(orient="records")
    except Exception as e:
        return []

@app.get("/api/run-etl")
def run_etl_endpoint():
    def event_stream():
        for log in ejecutar_etl():
            yield f"data: {log}\n\n"
    return StreamingResponse(event_stream(), media_type="text/event-stream")

os.makedirs("public", exist_ok=True)
app.mount("/", StaticFiles(directory="public", html=True), name="public")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
