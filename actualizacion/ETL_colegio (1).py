"""
ETL para Data Mart Academico - VERSIÓN ORIGINAL MEJORADA
"""

import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from datetime import datetime
import warnings
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

SQLSERVER_CONFIG = 'mssql+pyodbc://@localhost/datamart_colegio?driver=ODBC+Driver+17+for+SQL+Server'

mysql_engine = create_engine(f"mysql+pymysql://{MYSQL_CONFIG['user']}:{MYSQL_CONFIG['password']}@{MYSQL_CONFIG['host']}/{MYSQL_CONFIG['database']}")
sqlserver_engine = create_engine(SQLSERVER_CONFIG)

print("=" * 70)
print("INICIO DEL PROCESO ETL - VERSIÓN RÁPIDA")
print(f"Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 70)

# =============================================
# 1. EXTRACCION (Extract)
# =============================================

print("\n1. EXTRACCION DE DATOS DESDE MYSQL")

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
    asignaciones_df = pd.read_sql("SELECT * FROM asignaciones_profesor", mysql_engine)
    
    print(f"   Personas: {len(personas_df)} registros")
    print(f"   Estudiantes: {len(estudiantes_df)} registros")
    print(f"   Cursos: {len(cursos_df)} registros")
    print(f"   Matriculas: {len(matriculas_df)} registros")
    print(f"   Notas: {len(notas_df)} registros")
    print(f"   Asistencias: {len(asistencias_df)} registros")
    print(f"   Profesores: {len(profesores_df)} registros")
    print(f"   Asignaciones Docentes: {len(asignaciones_df)} registros")
    
except Exception as e:
    print(f"   Error en extraccion: {e}")
    exit()

# =============================================
# 2. TRANSFORMACION (Transform)
# =============================================

print("\n2. TRANSFORMACION DE DATOS")

# CONVERSION 1: DIMENSION ESTUDIANTE
print("   - CONVERSION 1: DimEstudiante")
dim_estudiante = estudiantes_df.merge(personas_df, left_on='persona_id', right_on='id')
dim_estudiante['nombre_completo'] = dim_estudiante['nombres'] + ' ' + dim_estudiante['apellidos']

temp_m = matriculas_df.merge(secciones_df, left_on='seccion_id', right_on='id').merge(grados_df, left_on='grado_id', right_on='id')
mapa_niveles = dict(zip(temp_m['estudiante_id'], temp_m['nombre'] + ' - ' + temp_m['nivel']))

dim_estudiante['grado_academico'] = dim_estudiante['id_x'].map(mapa_niveles).fillna('REGULAR')
dim_estudiante = dim_estudiante[['id_x', 'codigo_estudiante', 'nombre_completo', 'grado_academico']]
dim_estudiante.columns = ['id_estudiante_oltp', 'codigo_estudiante', 'nombre_completo', 'grado_academico']
dim_estudiante = dim_estudiante.reset_index(drop=True)

# CONVERSION 2: DIMENSION CURSO
print("   - CONVERSION 2: DimCurso")
dim_curso = cursos_df[['id', 'nombre', 'area']].copy()
dim_curso.columns = ['id_curso_oltp', 'nombre_curso', 'area_conocimiento']
dim_curso = dim_curso.reset_index(drop=True)

# CONVERSION 3: DIMENSION PROFESOR
print("   - CONVERSION 3: DimProfesor")
dim_profesor = profesores_df.merge(personas_df, left_on='persona_id', right_on='id')
dim_profesor['nombre_completo'] = dim_profesor['nombres'] + ' ' + dim_profesor['apellidos']
dim_profesor = dim_profesor[['id_x', 'nombre_completo', 'especialidad']]
dim_profesor.columns = ['id_profesor_oltp', 'nombre_completo', 'especialidad']
dim_profesor = dim_profesor.reset_index(drop=True)

# CONVERSION 4: DIMENSION GRADO SECCION
print("   - CONVERSION 4: DimGradoSeccion")
dim_grado_seccion = secciones_df.merge(grados_df, left_on='grado_id', right_on='id')
dim_grado_seccion['grado_estandarizado'] = dim_grado_seccion['nombre']
dim_grado_seccion = dim_grado_seccion[['grado_estandarizado', 'letra', 'turno', 'nivel']]
dim_grado_seccion.columns = ['grado', 'seccion', 'turno', 'nivel']
dim_grado_seccion = dim_grado_seccion.reset_index(drop=True)

# CONVERSION 5: DIMENSION TIEMPO
print("   - CONVERSION 5: DimTiempo")
fechas = pd.date_range(start='2020-01-01', end='2026-12-31', freq='D')

meses_es = {
    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio',
    7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
}

dim_tiempo = pd.DataFrame({
    'id_tiempo': range(1, len(fechas) + 1),
    'fecha': fechas,
    'anio': fechas.year,
    'mes': fechas.month,
    'nombre_mes': fechas.month.map(meses_es),
    'bimestre': ((fechas.month - 1) // 2) + 1
})

# =============================================
# 3. CARGA DE DIMENSIONES A SQL SERVER
# =============================================

print("\n3. CARGA DE DIMENSIONES A SQL SERVER")
try:
    with sqlserver_engine.connect() as conn:
        # Remover las restricciones
        for fk in ['FK_Hecho_DimTiempo', 'FK_Hecho_DimEstudiante', 'FK_Hecho_DimCurso', 'FK_Hecho_DimProfesor', 'FK_Hecho_DimGradoSeccion']:
            try:
                conn.execute(text(f"ALTER TABLE HechoRendimientoAcademico DROP CONSTRAINT {fk};"))
            except Exception:
                pass 
        
        # Vaciado completo
        conn.execute(text("TRUNCATE TABLE HechoRendimientoAcademico;"))
        conn.execute(text("TRUNCATE TABLE DimEstudiante;"))
        conn.execute(text("TRUNCATE TABLE DimCurso;"))
        conn.execute(text("TRUNCATE TABLE DimProfesor;"))
        conn.execute(text("TRUNCATE TABLE DimGradoSeccion;"))
        conn.execute(text("TRUNCATE TABLE DimTiempo;"))
        conn.commit()
    print("   - Dimensiones y hechos vaciados")
except Exception as e:
    print(f"   - Advertencia: {e}")

# Inserción de dimensiones
print("   - Cargando DimEstudiante...")
dim_estudiante.to_sql('DimEstudiante', sqlserver_engine, if_exists='append', index=False)

print("   - Cargando DimCurso...")
dim_curso.to_sql('DimCurso', sqlserver_engine, if_exists='append', index=False)

print("   - Cargando DimProfesor...")
dim_profesor.to_sql('DimProfesor', sqlserver_engine, if_exists='append', index=False)

print("   - Cargando DimGradoSeccion...")
dim_grado_seccion.to_sql('DimGradoSeccion', sqlserver_engine, if_exists='append', index=False)

print("   - Cargando DimTiempo...")
dim_tiempo.to_sql('DimTiempo', sqlserver_engine, if_exists='append', index=False)

# =============================================
# 4. OBTENER MAPEOS DE LLAVES SURROGADAS (SK)
# =============================================

print("\n4. OBTENIENDO MAPEOS DE CLAVES...")

df_estudiante_ids = pd.read_sql("SELECT id_estudiante_sk, id_estudiante_oltp FROM DimEstudiante", sqlserver_engine)
mapa_estudiante = dict(zip(df_estudiante_ids['id_estudiante_oltp'], df_estudiante_ids['id_estudiante_sk']))

df_curso_ids = pd.read_sql("SELECT id_curso_sk, id_curso_oltp FROM DimCurso", sqlserver_engine)
mapa_curso = dict(zip(df_curso_ids['id_curso_oltp'], df_curso_ids['id_curso_sk']))

df_profesor_ids = pd.read_sql("SELECT id_profesor_sk, id_profesor_oltp FROM DimProfesor", sqlserver_engine)
mapa_profesor = dict(zip(df_profesor_ids['id_profesor_oltp'], df_profesor_ids['id_profesor_sk']))

df_grado_ids = pd.read_sql("SELECT id_grado_seccion_sk, grado, seccion FROM DimGradoSeccion", sqlserver_engine)
mapa_grado = dict(zip(df_grado_ids['grado'] + '|' + df_grado_ids['seccion'], df_grado_ids['id_grado_seccion_sk']))

fecha_to_id = dict(zip(dim_tiempo['fecha'].dt.date, dim_tiempo['id_tiempo']))

# =============================================
# 5. TABLA DE HECHOS
# =============================================

print("\n5. PROCESANDO TABLA DE HECHOS...")

# Sanitizado de tipos
notas_df['matricula_id'] = notas_df['matricula_id'].astype(int)
matriculas_df['id'] = matriculas_df['id'].astype(int)
asignaciones_df['curso_id'] = asignaciones_df['curso_id'].astype(int)
asignaciones_df['seccion_id'] = asignaciones_df['seccion_id'].astype(int)
asignaciones_df['periodo_id'] = asignaciones_df['periodo_id'].astype(int)

# Eliminar duplicados
asignaciones_unicas = asignaciones_df.drop_duplicates(subset=['curso_id', 'seccion_id', 'periodo_id'])

# Unir notas con matrículas
print("   - Uniendo notas con matrículas...")
hecho = notas_df.merge(matriculas_df, left_on='matricula_id', right_on='id', suffixes=('', '_mat'))

# Unir con asignaciones
print("   - Uniendo con asignaciones...")
hecho = hecho.merge(asignaciones_unicas, on=['curso_id', 'seccion_id', 'periodo_id'], how='left')

# Unir con secciones y grados
print("   - Uniendo con secciones y grados...")
secciones_df['id'] = secciones_df['id'].astype(int)
grados_df['id'] = grados_df['id'].astype(int)
hecho = hecho.merge(secciones_df, left_on='seccion_id', right_on='id', suffixes=('', '_sec'))
hecho = hecho.merge(grados_df, left_on='grado_id', right_on='id', suffixes=('', '_grad'))

# Aplicar mapeos
print("   - Aplicando mapeos de claves...")
hecho['id_estudiante_sk'] = hecho['estudiante_id'].map(mapa_estudiante)
hecho['id_curso_sk'] = hecho['curso_id'].map(mapa_curso)
hecho['id_profesor_sk'] = hecho['profesor_id'].map(mapa_profesor).fillna(-1)

hecho['clave_gs_calculada'] = hecho['nombre'] + '|' + hecho['letra']
hecho['id_grado_seccion_sk'] = hecho['clave_gs_calculada'].map(mapa_grado)

hecho['fecha_limpia'] = pd.to_datetime(hecho['fecha_matricula']).dt.date
hecho['id_tiempo'] = hecho['fecha_limpia'].map(fecha_to_id).fillna(1).astype(int)

# Agregar asistencias
print("   - Agregando métricas de asistencia...")
if not asistencias_df.empty:
    asistencias_df['matricula_id'] = asistencias_df['matricula_id'].astype(int)
    asist_agregada = asistencias_df.groupby('matricula_id').agg(
        cantidad_asistencias=('estado', lambda x: sum(x.isin(['PRESENTE', 'TARDE']))),
        cantidad_tardanzas=('estado', lambda x: sum(x == 'TARDE')),
        cantidad_ausencias=('estado', lambda x: sum(x == 'FALTA_INJUSTIFICADA'))
    ).reset_index()
    hecho = hecho.merge(asist_agregada, on='matricula_id', how='left')
else:
    hecho['cantidad_asistencias'] = 0
    hecho['cantidad_tardanzas'] = 0
    hecho['cantidad_ausencias'] = 0

hecho['cantidad_asistencias'] = hecho['cantidad_asistencias'].fillna(0).astype(int)
hecho['cantidad_tardanzas'] = hecho['cantidad_tardanzas'].fillna(0).astype(int)
hecho['cantidad_ausencias'] = hecho['cantidad_ausencias'].fillna(0).astype(int)

# CORREGIDO: Obtener bimestre de manera dinámica
print("   - Procesando bimestre...")
col_bimestre = None
for col in hecho.columns:
    if 'bimestre' in col.lower():
        col_bimestre = col
        break

if col_bimestre:
    bimestre_valores = hecho[col_bimestre]
else:
    # Si no hay columna bimestre, calcular desde la fecha
    bimestre_valores = ((hecho['fecha_limpia'].dt.month - 1) // 2) + 1

# Crear hecho final
print("   - Creando dataframe final...")
hecho_final = pd.DataFrame({
    'id_tiempo': hecho['id_tiempo'],
    'id_estudiante_sk': hecho['id_estudiante_sk'],
    'id_curso_sk': hecho['id_curso_sk'],
    'id_profesor_sk': hecho['id_profesor_sk'],
    'id_grado_seccion_sk': hecho['id_grado_seccion_sk'],
    'bimestre': bimestre_valores,
    'nota_obtenida': hecho['valor'],
    'cantidad_asistencias': hecho['cantidad_asistencias'],
    'cantidad_tardanzas': hecho['cantidad_tardanzas'],
    'cantidad_ausencias': hecho['cantidad_ausencias']
})

# Limpiar registros huérfanos
print("   - Limpiando registros huérfanos...")
hecho_final = hecho_final.dropna(subset=['id_estudiante_sk', 'id_curso_sk', 'id_profesor_sk', 'id_grado_seccion_sk'])
hecho_final = hecho_final[hecho_final['id_profesor_sk'] != -1]

hecho_final['id_estudiante_sk'] = hecho_final['id_estudiante_sk'].astype(int)
hecho_final['id_curso_sk'] = hecho_final['id_curso_sk'].astype(int)
hecho_final['id_profesor_sk'] = hecho_final['id_profesor_sk'].astype(int)
hecho_final['id_grado_seccion_sk'] = hecho_final['id_grado_seccion_sk'].astype(int)

print(f"   - Registros listos: {len(hecho_final):,}")

# =============================================
# 6. CARGA FINAL DE HECHOS
# =============================================

print("\n6. CARGANDO TABLA DE HECHOS...")

try:
    # Carga directa (más rápida)
    hecho_final.to_sql('HechoRendimientoAcademico', sqlserver_engine, if_exists='append', index=False)
    print(f"   ✓ Cargados {len(hecho_final):,} registros en HechoRendimientoAcademico.")
except Exception as e:
    print(f"   Error cargando hechos: {e}")
    
    # Si falla la carga directa, intentar por lotes
    print("   Intentando carga por lotes...")
    batch_size = 50000
    total = len(hecho_final)
    for i in range(0, total, batch_size):
        batch = hecho_final.iloc[i:i+batch_size]
        batch.to_sql('HechoRendimientoAcademico', sqlserver_engine, if_exists='append', index=False)
        print(f"   Cargados {min(i+batch_size, total):,}/{total:,} registros")

# Reconstruir constraints
print("\n7. RECONSTRUYENDO CONSTRAINTS...")
try:
    with sqlserver_engine.connect() as conn:
        conn.execute(text("ALTER TABLE HechoRendimientoAcademico ADD CONSTRAINT FK_Hecho_DimTiempo FOREIGN KEY (id_tiempo) REFERENCES DimTiempo(id_tiempo);"))
        conn.execute(text("ALTER TABLE HechoRendimientoAcademico ADD CONSTRAINT FK_Hecho_DimEstudiante FOREIGN KEY (id_estudiante_sk) REFERENCES DimEstudiante(id_estudiante_sk);"))
        conn.execute(text("ALTER TABLE HechoRendimientoAcademico ADD CONSTRAINT FK_Hecho_DimCurso FOREIGN KEY (id_curso_sk) REFERENCES DimCurso(id_curso_sk);"))
        conn.execute(text("ALTER TABLE HechoRendimientoAcademico ADD CONSTRAINT FK_Hecho_DimProfesor FOREIGN KEY (id_profesor_sk) REFERENCES DimProfesor(id_profesor_sk);"))
        conn.execute(text("ALTER TABLE HechoRendimientoAcademico ADD CONSTRAINT FK_Hecho_DimGradoSeccion FOREIGN KEY (id_grado_seccion_sk) REFERENCES DimGradoSeccion(id_grado_seccion_sk);"))
        conn.commit()
    print("   ✓ Constraints restauradas.")
except Exception as e:
    print(f"   Advertencia: {e}")

# =============================================
# 8. RESUMEN FINAL
# =============================================

print("\n" + "=" * 70)
print("PROCESO ETL FINALIZADO CON ÉXITO")
print("=" * 70)

# Mostrar resumen
try:
    resumen = pd.read_sql("""
        SELECT 
            (SELECT COUNT(*) FROM DimEstudiante) AS Estudiantes,
            (SELECT COUNT(*) FROM DimCurso) AS Cursos,
            (SELECT COUNT(*) FROM DimProfesor) AS Profesores,
            (SELECT COUNT(*) FROM DimGradoSeccion) AS GradosSecciones,
            (SELECT COUNT(*) FROM DimTiempo) AS Tiempo,
            (SELECT COUNT(*) FROM HechoRendimientoAcademico) AS RegistrosHecho
    """, sqlserver_engine)
    
    print("\nRESUMEN DE CARGA:")
    for col in resumen.columns:
        print(f"   {col}: {resumen[col].iloc[0]:,}")
except Exception as e:
    print(f"   No se pudo obtener resumen: {e}")

print("=" * 70)