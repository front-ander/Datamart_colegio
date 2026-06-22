"""
ETL para Data Mart Academico (Refactorizado para Web UI)
Origen: MySQL (bd_colegio)
Destino: SQL Server (datamart_colegio)
"""

import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from datetime import datetime
import warnings
import json
import traceback
import time

warnings.filterwarnings('ignore')

# =============================================
# CONFIGURACION DE CONEXIONES
# =============================================
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'ccole'
}
SQLSERVER_CONFIG = 'mssql+pyodbc://localhost/Datamart_colegio?driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes'

def emitir_evento(nodo, estado, mensaje, filas=0):
    """Genera un string JSON para enviar al frontend."""
    evento = {
        "node": nodo,
        "status": estado,
        "message": mensaje,
        "rows": filas,
        "time": datetime.now().strftime('%H:%M:%S')
    }
    return json.dumps(evento) + "\n"

def connect_with_retry(engine_url, max_retries=3, delay=5):
    """Intenta conectar a la base de datos con reintentos para resiliencia."""
    engine = create_engine(engine_url)
    last_exception = None
    for attempt in range(1, max_retries + 1):
        try:
            with engine.connect() as conn:
                pass # Solo probar la conexión
            return engine
        except Exception as e:
            last_exception = e
            time.sleep(delay)
    raise Exception(f"Fallo de conexión tras {max_retries} intentos. Error: {str(last_exception)}")

def ejecutar_etl():
    """Generador que ejecuta el ETL paso a paso y emite el progreso."""
    
    yield emitir_evento("System", "info", "Inicializando conexiones con resiliencia...")
    
    # Crear conexiones con reintentos
    mysql_url = f"mysql+pymysql://{MYSQL_CONFIG['user']}:{MYSQL_CONFIG['password']}@{MYSQL_CONFIG['host']}/{MYSQL_CONFIG['database']}"
    try:
        mysql_engine = connect_with_retry(mysql_url)
        sqlserver_engine = connect_with_retry(SQLSERVER_CONFIG)
    except Exception as e:
        yield emitir_evento("System", "error", f"Error crítico de conexión: {str(e)}")
        return
    
    yield emitir_evento("System", "info", "Iniciando proceso ETL...")

    # =============================================
    # 1. EXTRACCION
    # =============================================
    yield emitir_evento("Extract_MySQL", "running", "Extrayendo datos de MySQL...")
    try:
        personas_df = pd.read_sql("SELECT * FROM personas", mysql_engine)
        estudiantes_df = pd.read_sql("SELECT * FROM estudiantes", mysql_engine)
        cursos_df = pd.read_sql("SELECT * FROM cursos", mysql_engine)
        matriculas_df = pd.read_sql("SELECT * FROM matriculas", mysql_engine)
        notas_df = pd.read_sql("SELECT * FROM notas", mysql_engine)
        asistencias_df = pd.read_sql("SELECT * FROM asistencias_estudiantes", mysql_engine)
        profesores_df = pd.read_sql("SELECT * FROM profesores", mysql_engine)
        grados_df = pd.read_sql("SELECT * FROM grados", mysql_engine)
        secciones_df = pd.read_sql("SELECT * FROM secciones", mysql_engine)
        
        total_extraccion = len(personas_df) + len(estudiantes_df) + len(cursos_df) + len(matriculas_df) + len(notas_df) + len(asistencias_df) + len(profesores_df)
        yield emitir_evento("Extract_MySQL", "success", "Extracción completada", total_extraccion)
    except Exception as e:
        yield emitir_evento("Extract_MySQL", "error", f"Error en extracción: {str(e)}")
        return

    # =============================================
    # 2. TRANSFORMACION
    # =============================================
    yield emitir_evento("Transform_Data", "running", "Transformando dimensiones...")
    
    # DimEstudiante
    dim_estudiante = estudiantes_df.merge(personas_df, left_on='persona_id', right_on='id')
    dim_estudiante['nombre_completo'] = dim_estudiante['nombres'] + ' ' + dim_estudiante['apellidos']
    dim_estudiante['grado_academico'] = 'PRIMARIA'
    dim_estudiante = dim_estudiante[['id_x', 'codigo_estudiante', 'nombre_completo', 'grado_academico']]
    dim_estudiante.columns = ['id_estudiante_oltp', 'codigo_estudiante', 'nombre_completo', 'grado_academico']
    
    # DimCurso
    dim_curso = cursos_df[['id', 'nombre', 'area']].copy()
    dim_curso.columns = ['id_curso_oltp', 'nombre_curso', 'area_conocimiento']
    dim_curso['area_conocimiento'] = dim_curso['area_conocimiento'].fillna('GENERAL')
    
    # DimProfesor
    if len(profesores_df) > 0:
        dim_profesor = profesores_df.merge(personas_df, left_on='persona_id', right_on='id')
        dim_profesor['nombre_completo'] = dim_profesor['nombres'] + ' ' + dim_profesor['apellidos']
        dim_profesor = dim_profesor[['id_x', 'nombre_completo', 'especialidad']]
        dim_profesor.columns = ['id_profesor_oltp', 'nombre_completo', 'especialidad']
    else:
        dim_profesor = pd.DataFrame({'id_profesor_oltp': [1], 'nombre_completo': ['Profesor General'], 'especialidad': ['GENERAL']})
    
    # DimGradoSeccion
    if len(secciones_df) > 0 and len(grados_df) > 0:
        dim_grado_seccion = secciones_df.merge(grados_df, left_on='grado_id', right_on='id')
        dim_grado_seccion['grado_estandarizado'] = dim_grado_seccion['nombre'] + ' - ' + dim_grado_seccion['nivel']
        dim_grado_seccion = dim_grado_seccion[['grado_estandarizado', 'letra', 'turno', 'nivel']]
        dim_grado_seccion.columns = ['grado', 'seccion', 'turno', 'nivel']
    else:
        dim_grado_seccion = pd.DataFrame({'grado': ['PRIMERO - PRIMARIA'], 'seccion': ['A'], 'turno': ['MAÑANA'], 'nivel': ['PRIMARIA']})
    
    # DimTiempo
    fechas = pd.date_range(start='2020-01-01', end='2026-12-31', freq='D')
    dim_tiempo = pd.DataFrame({
        'id_tiempo': range(1, len(fechas) + 1),
        'fecha': fechas,
        'anio': fechas.year, 'mes': fechas.month,
        'nombre_mes': fechas.strftime('%B'),
        'bimestre': ((fechas.month - 1) // 2) + 1
    })

    yield emitir_evento("Transform_Data", "success", "Transformación en memoria completada")

    # =============================================
    # 3. LIMPIEZA DESTINO
    # =============================================
    yield emitir_evento("Clean_Dest", "running", "Limpiando tablas destino...")
    try:
        with sqlserver_engine.connect() as conn:
            conn.execute(text("DELETE FROM HechoRendimientoAcademico"))
            conn.execute(text("DELETE FROM DimEstudiante"))
            conn.execute(text("DELETE FROM DimCurso"))
            conn.execute(text("DELETE FROM DimProfesor"))
            conn.execute(text("DELETE FROM DimGradoSeccion"))
            conn.execute(text("DELETE FROM DimTiempo"))
            conn.commit()
        yield emitir_evento("Clean_Dest", "success", "Tablas limpiadas correctamente")
    except Exception as e:
        yield emitir_evento("Clean_Dest", "warning", f"Aviso limpieza: {str(e)}")

    # =============================================
    # 4. CARGA DE DIMENSIONES
    # =============================================
    
    def cargar_dimension(nombre_nodo, nombre_tabla, df):
        yield emitir_evento(nombre_nodo, "running", f"Cargando {nombre_tabla}...")
        df.to_sql(nombre_tabla, sqlserver_engine, if_exists='append', index=False)
        yield emitir_evento(nombre_nodo, "success", f"{nombre_tabla} cargada", len(df))

    try:
        yield from cargar_dimension("Load_DimEstudiante", "DimEstudiante", dim_estudiante)
        yield from cargar_dimension("Load_DimCurso", "DimCurso", dim_curso)
        yield from cargar_dimension("Load_DimProfesor", "DimProfesor", dim_profesor)
        yield from cargar_dimension("Load_DimGrado", "DimGradoSeccion", dim_grado_seccion)
        yield from cargar_dimension("Load_DimTiempo", "DimTiempo", dim_tiempo)
    except Exception as e:
        yield emitir_evento("Load_Dimensions", "error", f"Error cargando dimensiones: {str(e)}")
        return

    # =============================================
    # 5. GENERAR HECHOS Y MAPEOS
    # =============================================
    yield emitir_evento("Mapping_Facts", "running", "Obteniendo SKs y procesando Hechos...")
    try:
        # Obtener mapeos
        df_estudiante_ids = pd.read_sql("SELECT id_estudiante_sk, id_estudiante_oltp FROM DimEstudiante", sqlserver_engine)
        mapa_estudiante = dict(zip(df_estudiante_ids['id_estudiante_oltp'], df_estudiante_ids['id_estudiante_sk']))
        
        df_curso_ids = pd.read_sql("SELECT id_curso_sk, id_curso_oltp FROM DimCurso", sqlserver_engine)
        mapa_curso = dict(zip(df_curso_ids['id_curso_oltp'], df_curso_ids['id_curso_sk']))
        
        df_grado_ids = pd.read_sql("SELECT id_grado_seccion_sk, grado, seccion FROM DimGradoSeccion", sqlserver_engine)
        df_grado_ids['clave'] = df_grado_ids['grado'] + '|' + df_grado_ids['seccion']
        mapa_grado = {row['clave']: row['id_grado_seccion_sk'] for _, row in df_grado_ids.iterrows()}
        
        df_profesor_ids = pd.read_sql("SELECT id_profesor_sk, id_profesor_oltp FROM DimProfesor", sqlserver_engine)
        mapa_profesor = dict(zip(df_profesor_ids['id_profesor_oltp'], df_profesor_ids['id_profesor_sk']))

        # Procesar hechos
        hecho = notas_df.merge(matriculas_df, left_on='matricula_id', right_on='id')
        hecho = hecho.merge(estudiantes_df, left_on='estudiante_id', right_on='id')
        
        hecho['id_estudiante_sk'] = hecho['estudiante_id'].map(mapa_estudiante)
        hecho['id_curso_sk'] = hecho['curso_id'].map(mapa_curso)
        
        hecho['id_profesor_sk'] = 1
        if len(mapa_profesor) > 0:
            hecho['id_profesor_sk'] = hecho.get('profesor_id', pd.Series([1]*len(hecho))).map(mapa_profesor).fillna(1).astype(int)

        hecho['clave_grado'] = 'PRIMERO - PRIMARIA|A'
        if len(secciones_df) > 0 and len(grados_df) > 0:
            hecho_temp = hecho.merge(matriculas_df[['id', 'seccion_id']], left_on='matricula_id', right_on='id', suffixes=('', '_matricula'))
            if 'seccion_id' in hecho_temp.columns:
                for idx, row in secciones_df.iterrows():
                    grado_nombre = grados_df[grados_df['id'] == row['grado_id']]['nombre'].values
                    if len(grado_nombre) > 0:
                        clave = f"{grado_nombre[0]} - {grados_df[grados_df['id'] == row['grado_id']]['nivel'].values[0]}|{row['letra']}"
                        hecho.loc[hecho_temp['seccion_id'] == row['id'], 'clave_grado'] = clave

        hecho['id_grado_seccion_sk'] = hecho['clave_grado'].map(mapa_grado).fillna(1).astype(int)

        if 'fecha_matricula' in hecho.columns:
            hecho['fecha'] = pd.to_datetime(hecho['fecha_matricula']).dt.date
        else:
            hecho['fecha'] = datetime.now().date()

        fecha_to_id = dict(zip(dim_tiempo['fecha'].dt.date, dim_tiempo['id_tiempo']))
        hecho['id_tiempo'] = hecho['fecha'].map(fecha_to_id).fillna(1).astype(int)

        if not asistencias_df.empty:
            asistencia_agregada = asistencias_df.groupby('matricula_id').agg(
                cantidad_asistencias=('estado', lambda x: sum(x.isin(['PRESENTE', 'TARDE']))),
                cantidad_tardanzas=('estado', lambda x: sum(x == 'TARDE')),
                cantidad_ausencias=('estado', lambda x: sum(x == 'FALTA_INJUSTIFICADA'))
            ).reset_index()
            hecho = hecho.merge(asistencia_agregada, left_on='matricula_id', right_on='matricula_id', how='left')
        else:
            hecho['cantidad_asistencias'] = 0
            hecho['cantidad_tardanzas'] = 0
            hecho['cantidad_ausencias'] = 0

        hecho['cantidad_asistencias'] = hecho['cantidad_asistencias'].fillna(0)
        hecho['cantidad_tardanzas'] = hecho['cantidad_tardanzas'].fillna(0)
        hecho['cantidad_ausencias'] = hecho['cantidad_ausencias'].fillna(0)

        hecho_final = pd.DataFrame({
            'id_tiempo': hecho['id_tiempo'],
            'id_estudiante_sk': hecho['id_estudiante_sk'],
            'id_curso_sk': hecho['id_curso_sk'],
            'id_profesor_sk': hecho['id_profesor_sk'],
            'id_grado_seccion_sk': hecho['id_grado_seccion_sk'],
            'bimestre': hecho['bimestre_x'] if 'bimestre_x' in hecho.columns else 1,
            'nota_obtenida': hecho['valor'],
            'cantidad_asistencias': hecho['cantidad_asistencias'],
            'cantidad_tardanzas': hecho['cantidad_tardanzas'],
            'cantidad_ausencias': hecho['cantidad_ausencias']
        })

        hecho_final = hecho_final.dropna(subset=['nota_obtenida', 'id_estudiante_sk', 'id_curso_sk'])
        hecho_final['nota_obtenida'] = hecho_final['nota_obtenida'].astype(float)
        hecho_final['id_estudiante_sk'] = hecho_final['id_estudiante_sk'].astype(int)
        hecho_final['id_curso_sk'] = hecho_final['id_curso_sk'].astype(int)

        yield emitir_evento("Mapping_Facts", "success", "Procesamiento de hechos terminado")
        
        yield emitir_evento("Load_Hecho", "running", "Cargando HechoRendimientoAcademico...")
        hecho_final.to_sql('HechoRendimientoAcademico', sqlserver_engine, if_exists='append', index=False)
        yield emitir_evento("Load_Hecho", "success", "Hechos cargados", len(hecho_final))

    except Exception as e:
        yield emitir_evento("Mapping_Facts", "error", f"Error en procesamiento: {traceback.format_exc()}")
        return

    yield emitir_evento("System", "success", "¡PROCESO ETL COMPLETADO EXITOSAMENTE!")

if __name__ == "__main__":
    for msg in ejecutar_etl():
        print(msg.strip())