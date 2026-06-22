import random
import pymysql
import re
from datetime import datetime, timedelta

# Conexión centralizada a la base transaccional original
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    database='ccole',
    autocommit=False  # Desactivado para controlar manualmente confirmaciones masivas (Bulk)
)
cursor = conn.cursor()

print("==================================================")
print("INICIANDO GENERACIÓN DE DATA INTEGRAL (OLTP 2026)")
print("==================================================")

# ==================================================
# 1. ARRAYS DE NOMBRES, APELLIDOS Y CATÁLOGOS BASE
# ==================================================
nombres_hombres = [
    'Kevin', 'Carlos', 'Luis', 'Juan', 'Jorge', 'Pedro', 'Miguel', 'Angel', 
    'Diego', 'Alejandro', 'Jose', 'Christian', 'Manuel', 'Ricardo', 'Fernando',
    'David', 'Santiago', 'Sebastian', 'Mateo', 'Gabriel', 'Lucas', 'Daniel', 
    'Eduardo', 'Alonso', 'Rodrigo', 'Gonzalo', 'Mauricio', 'Javier', 'Arturo', 
    'Enrique', 'César', 'Iván', 'Gustavo', 'Héctor', 'Fabrizio', 'Renato', 
    'Josué', 'Samuel', 'Alexander', 'Aaron', 'Anthony', 'Jean', 'Bryan',
    'Leonardo', 'Matías', 'Álvaro', 'Andrés', 'Hugo', 'Marcos', 'Víctor'
]

nombres_mujeres = [
    'Camila', 'Maria', 'Ana', 'Lucia', 'Sofía', 'Laura', 'Elena', 'Gabriela', 
    'Valeria', 'Claudia', 'Paola', 'Andrea', 'Milagros', 'Fiorella', 'Natalia',
    'Daniela', 'Isabella', 'Valentina', 'Alejandra', 'Diana', 'Beatriz', 'Ximena', 
    'Adriana', 'Luciana', 'Fernanda', 'Carolina', 'Mariana', 'Vanessa', 'Jessica', 
    'Karla', 'Cecilia', 'Roxana', 'Liliana', 'Patricia', 'Rosa', 'Carmen', 
    'Elizabeth', 'Angélica', 'Nicole', 'Melany', 'Estefany', 'Kiara', 'Bianca',
    'Giselle', 'Valerie', 'Camille', 'Alessandra', 'Fabiola', 'Tatiana', 'Ariadna'
]

apellidos = [
    'García', 'Mendoza', 'Rodríguez', 'López', 'Martínez', 'Pérez', 'Gómez', 
    'Sánchez', 'Díaz', 'Torres', 'Ramírez', 'Flores', 'Castro', 'Romero', 
    'Quispe', 'Gonzales', 'Chávez', 'Espinoza', 'Ramos', 'Fernández', 'Silva', 
    'Rojas', 'Herrera', 'Palomino', 'Gutiérrez', 'Vargas', 'Vásquez', 'Castillo', 
    'Yarlequé', 'Sullón', 'Vilchez', 'Sandoval', 'Farfán', 'Campos', 'Guerrero',
    'Zapata', 'Agurto', 'Garrido', 'Saavedra', 'Correa', 'Moreno', 'Pacherres',
    'Panta', 'Navarro', 'Salinas', 'Pingo', 'Seminario', 'Olaya', 'Juárez'
]

dnis_generados = set()
correos_generados = set()
usernames_generados = set()

def generar_dni_unico():
    while True:
        dni = "".join([str(random.randint(0, 9)) for _ in range(8)])
        if dni not in dnis_generados:
            dnis_generados.add(dni)
            return dni

def generar_celular_peruano():
    return "9" + "".join([str(random.randint(0, 9)) for _ in range(8)])

def limpiar_texto_correo(texto):
    texto = texto.lower().strip()
    texto = re.sub(r'[áàäâ]', 'a', texto)
    texto = re.sub(r'[éèëê]', 'e', texto)
    texto = re.sub(r'[íìïî]', 'i', texto)
    texto = re.sub(r'[óòöô]', 'o', texto)
    texto = re.sub(r'[úùüû]', 'u', texto)
    texto = re.sub(r'[ñ]', 'n', texto)
    return re.sub(r'[^a-z0-9]', '', texto)

def generar_correo_unico(nombre, apellido, sufijo):
    primer_nom = limpiar_texto_correo(nombre.split()[0])
    primer_ape = limpiar_texto_correo(apellido.split()[0])
    sufijo_clean = limpiar_texto_correo(sufijo)
    base_correo = f"{primer_nom}.{primer_ape}.{sufijo_clean}" if sufijo_clean else f"{primer_nom}.{primer_ape}"
    correo = f"{base_correo}@milagros.edu.pe"
    contador = 1
    while correo in correos_generados:
        correo = f"{base_correo}{contador}@milagros.edu.pe"
        contador += 1
    correos_generados.add(correo)
    return correo

def crear_usuario_sistema(nombre, apellido, rol_id):
    p_nom = limpiar_texto_correo(nombre.split()[0])
    p_ape = limpiar_texto_correo(apellido.split()[0])
    username = f"{p_nom}.{p_ape}"
    contador = 1
    while username in usernames_generados:
        username = f"{p_nom}.{p_ape}{contador}"
        contador += 1
    usernames_generados.add(username)
    
    # Hash genérico simulado para agilidad del insert
    pwd_hash = "$2y$10$M7b2Y8XGzZ7R9bC5dE6f7uG8hI9jK0lM1nO2pQ3rS4tU5vW6xYyZi"
    cursor.execute("INSERT INTO usuarios (username, password_hash, rol_id, estado) VALUES (%s, %s, %s, 'ACTIVO')", (username, pwd_hash, rol_id))
    return cursor.lastrowid

# ==================================================
# 2. LIMPIEZA RIGUROSA BAJO RESTRICCIONES DE LLAVES
# ==================================================
print("-> Ejecutando purga total de datos previos...")
cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
tablas_sistema = [
    'prestamos_biblioteca', 'libros', 'inventario_equipos', 'fichas_medicas', 
    'atenciones_enfermeria', 'reportes_disciplinarios', 'pagos', 'notas', 
    'asistencias_estudiantes', 'asignaciones_profesor', 'matriculas', 'estudiantes', 
    'profesores', 'personas', 'usuarios', 'roles', 'secciones', 'grados', 
    'cursos', 'periodos_academicos'
]
for tabla in tablas_sistema:
    cursor.execute(f"DELETE FROM `{tabla}`;")
    cursor.execute(f"ALTER TABLE `{tabla}` AUTO_INCREMENT = 1;")
cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
conn.commit()

# ==================================================
# 3. POBLADO DE CATÁLOGOS E INFRAESTRUCTURA BASE
# ==================================================
print("-> Configurando roles y periodo lectivo 2026...")
cursor.execute("INSERT INTO roles (nombre) VALUES ('ADMIN'), ('DOCENTE'), ('ESTUDIANTE')")
cursor.execute("SELECT id, nombre FROM roles")
mapa_roles = {row[1]: row[0] for row in cursor.fetchall()}

cursor.execute("INSERT INTO periodos_academicos (anio, fecha_inicio, fecha_fin, estado) VALUES (2026, '2026-03-02', '2026-12-18', 'ACTIVO')")
periodo_id = cursor.lastrowid

# Generación de la grilla de Grados e Infraestructura de Aulas (Secciones A y B)
for g in range(1, 7):
    cursor.execute(f"INSERT INTO grados (nombre, nivel) VALUES ('{g}to PRIMARIA', 'PRIMARIA')")
for g in range(1, 6):
    cursor.execute(f"INSERT INTO grados (nombre, nivel) VALUES ('{g}to SECUNDARIA', 'SECUNDARIA')")

cursor.execute("SELECT id, nivel, nombre FROM grados")
for gd in cursor.fetchall():
    cursor.execute(f"INSERT INTO secciones (grado_id, letra, turno) VALUES ({gd[0]}, 'A', 'MAÑANA')")
    cursor.execute(f"INSERT INTO secciones (grado_id, letra, turno) VALUES ({gd[0]}, 'B', 'MAÑANA')")

cursor.execute("SELECT s.id, g.nombre, s.letra FROM secciones s JOIN grados g ON s.grado_id = g.id")
secciones_db = cursor.fetchall()

cursos_definicion = [
    ('Matemática', 'CIENCIAS'), ('Comunicación', 'LETRAS'), ('Ciencia y Ambiente', 'CIENCIAS'),
    ('CTA (Física/Química)', 'CIENCIAS'), ('Personal Social', 'LETRAS'), ('Religión', 'LETRAS'),
    ('Computación', 'TECNOLOGÍA'), ('Arte', 'ARTE'), ('Educación Física', 'DEPORTE'), ('Inglés', 'IDIOMAS')
]
mapa_cursos_ids = {}
for nom_c, area_c in cursos_definicion:
    cursor.execute(f"INSERT INTO cursos (nombre, area) VALUES ('{nom_c}', '{area_c}')")
    mapa_cursos_ids[nom_c] = cursor.lastrowid

# ==================================================
# 4. CREACIÓN DEL CUERPO DOCENTE Y PLAN DE ESTUDIOS
# ==================================================
def crear_docente(genero, especialidad, indice):
    nom = random.choice(nombres_hombres) if genero == 'H' else random.choice(nombres_mujeres)
    nom2 = random.choice(nombres_hombres) if genero == 'H' else random.choice(nombres_mujeres)
    ape = f"{random.choice(apellidos)} {random.choice(apellidos)}"
    
    u_id = crear_usuario_sistema(nom, ape, mapa_roles['DOCENTE'])
    dni_val = generar_dni_unico()
    telf_val = generar_celular_peruano()
    correo_val = generar_correo_unico(nom, ape, "edu")
    fecha_nac = f"{random.randint(1972, 1993)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
    
    cursor.execute("""
        INSERT INTO personas (usuario_id, dni, nombres, apellidos, fecha_nacimiento, telefono, email) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (u_id, dni_val, f"{nom} {nom2}", ape, fecha_nac, telf_val, correo_val))
    p_id = cursor.lastrowid
    
    cod_prof = f"PROFE-2026{indice:02d}"
    cursor.execute("INSERT INTO profesores (persona_id, codigo_profesor, especialidad) VALUES (%s, %s, %s)", (p_id, cod_prof, especialidad))
    return cursor.lastrowid

profesores = {
    'mat_prim_baja': crear_docente('H', 'Lic. en Educación Primaria - Mención Ciencias', 1),
    'mat_prim_alta': crear_docente('M', 'Lic. en Ciencias Matemáticas y Primaria', 2),
    'tutor_prim_1': crear_docente('M', 'Educación Primaria', 3),
    'tutor_prim_2': crear_docente('H', 'Educación Primaria', 4),
    'tutor_prim_3': crear_docente('M', 'Educación Primaria', 5),
    'tutor_prim_4': crear_docente('H', 'Educación Primaria', 6),
    'mat_sec_baja': crear_docente('H', 'Lic. en Educación Secundaria: Matemática', 7),
    'mat_sec_alta': crear_docente('H', 'Lic. en Educación Secundaria: Matemática y Física', 8),
    'quim_fis': crear_docente('M', 'Ingeniero Químico con Especialización Pedagógica', 9),
    'ingles_sec': crear_docente('M', 'Lic. en Idiomas Extranjeros: Inglés', 10),
    'comu_sec': crear_docente('M', 'Lic. en Educación Secundaria: Lengua y Literatura', 11),
    'cta_soc_sec': crear_docente('H', 'Lic. en Educación: Biología y Química', 12),
    'rel_sec': crear_docente('M', 'Lic. en Educación: Sciences Religiosas', 13),
    'comp_sec': crear_docente('H', 'Ingeniero de Sistemas e Informática', 14),
    'arte_sec': crear_docente('M', 'Lic. en Pedagogía del Arte y Cultura', 15),
    'ed_fis_sec': crear_docente('H', 'Lic. en Educación Física y Deportes', 16)
}

# Asignaciones Horarias
for sec_id, g_nom, s_letra in secciones_db:
    num_grado = int(g_nom[0])
    g_nivel = 'PRIMARIA' if 'PRIMARIA' in g_nom else 'SECUNDARIA'
    cursos_a_asignar = ['Matemática', 'Comunicación', 'Personal Social', 'Religión', 'Computación', 'Arte', 'Educación Física', 'Inglés']
    cursos_a_asignar.append('Ciencia y Ambiente' if g_nivel == 'PRIMARIA' else 'CTA (Física/Química)')
    
    for c_nom in cursos_a_asignar:
        c_id = mapa_cursos_ids[c_nom]
        if c_nom == 'Matemática':
            if g_nivel == 'PRIMARIA':
                prof_id = profesores['mat_prim_baja'] if num_grado <= 2 else profesores['mat_prim_alta']
            else:
                prof_id = profesores['mat_sec_baja'] if num_grado <= 3 else profesores['mat_sec_alta']
        elif c_nom == 'CTA (Física/Química)':
            prof_id = profesores['quim_fis'] if num_grado >= 4 else profesores['cta_soc_sec']
        elif c_nom == 'Inglés': prof_id = profesores['ingles_sec']
        elif c_nom == 'Comunicación': prof_id = profesores['comu_sec']
        elif c_nom == 'Educación Física': prof_id = profesores['ed_fis_sec']
        elif c_nom == 'Computación': prof_id = profesores['comp_sec']
        elif c_nom == 'Arte': prof_id = profesores['arte_sec']
        elif c_nom == 'Religión': prof_id = profesores['rel_sec']
        else:
            prof_id = profesores['tutor_prim_1'] if g_nivel == 'PRIMARIA' else profesores['cta_soc_sec']
            
        cursor.execute("INSERT INTO asignaciones_profesor (profesor_id, curso_id, seccion_id, periodo_id) VALUES (%s, %s, %s, %s)", (prof_id, c_id, sec_id, periodo_id))
conn.commit()

# ==================================================
# 5. POBLADO AUXILIAR: LIBROS E INVENTARIO DE EQUIPOS
# ==================================================
print("-> Insertando catálogo de biblioteca e inventario patrimonial...")
libros_data = [
    ('9786123164123', 'Álgebra de Baldor', 'Aurelio Baldor', 'Matemáticas', 25, 25),
    ('9788420655659', 'Don Quijote de la Mancha', 'Miguel de Cervantes', 'Literatura', 30, 30),
    ('9786124256112', 'Tradiciones Peruanas', 'Ricardo Palma', 'Historia/Literatura', 20, 20),
    ('9789501245630', 'Pedagogía del Oprimido', 'Paulo Freire', 'Educación', 5, 5),
    ('9786123172029', 'Física Universitaria', 'Sears Zemansky', 'Física', 15, 15)
]
cursor.executemany("INSERT INTO libros (codigo_isbn, titulo, autor, categoria, stock_total, stock_disponible) VALUES (%s, %s, %s, %s, %s, %s)", libros_data)
libros_ids = [i for i in range(1, len(libros_data)+1)]

for s_id, g_nom, s_letra in secciones_db:
    cod_pat = f"PAT-2026-AULA-{s_id:02d}"
    cursor.execute("""
        INSERT INTO inventario_equipos (codigo_patrimonial, categoria, descripcion, estado, fecha_adquisicion, valor_adquisicion, ubicacion) 
        VALUES (%s, 'TECNOLOGÍA', 'Proyector Multimedia Epson Classroom', 'BUENO', '2026-01-15', 2450.00, %s)
    """, (cod_pat, f"Aula {g_nom} {s_letra}"))
conn.commit()

# ==================================================
# 6. GENERACIÓN MASIVA PRINCIPAL (1500 ALUMNOS)
# ==================================================
total_alumnos = 1500
print(f"-> Generando {total_alumnos} perfiles estudiantiles y transacciones asociadas...")

tipos_evaluacion = ['EXAMEN_PARCIAL', 'EXAMEN_FINAL', 'PRACTICA', 'TAREA']
tipos_sangre = ['O+', 'O-', 'A+', 'B+']
alergias_opc = ['Ninguna', 'Penicilina', 'Polvo/Ácaros', 'Gluten']

# Arrays para recopilar inserciones masivas optimizadas (Bulk inserts)
bulk_notas = []
bulk_fichas = []
bulk_pagos = []

# Mapeo de alumnos para transacciones cruzadas posteriores
estudiantes_mapeados = [] # guardará tuplas (estudiante_id, matricula_id, persona_id, seccion_id)

for i in range(total_alumnos):
    genero = random.choice(['H', 'M'])
    nom = random.choice(nombres_hombres) if genero == 'H' else random.choice(nombres_mujeres)
    nom2 = random.choice(nombres_hombres) if genero == 'H' else random.choice(nombres_mujeres)
    ape = f"{random.choice(apellidos)} {random.choice(apellidos)}"
    
    u_id = crear_usuario_sistema(nom, ape, mapa_roles['ESTUDIANTE'])
    sec_id, g_nom, s_letra = random.choice(secciones_db)
    
    abreviatura_nivel = "p" if "PRIMARIA" in g_nom else "s"
    string_seccion = f"{g_nom[0]}{abreviatura_nivel}{s_letra}"
    
    dni_val = generar_dni_unico()
    telf_val = generar_celular_peruano()
    correo_val = generar_correo_unico(nom, ape, string_seccion)
    fecha_nac_est = f"{random.randint(2010, 2019)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
    
    cursor.execute("""
        INSERT INTO personas (usuario_id, dni, nombres, apellidos, fecha_nacimiento, telefono, email) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (u_id, dni_val, f"{nom} {nom2}", ape, fecha_nac_est, telf_val, correo_val))
    p_id = cursor.lastrowid
    
    cod_est = f"EST-2026{i:04d}"
    cursor.execute("INSERT INTO estudiantes (persona_id, codigo_estudiante, fecha_ingreso) VALUES (%s, %s, '2026-03-02')", (p_id, cod_est))
    est_id = cursor.lastrowid
    
    cursor.execute("INSERT INTO matriculas (estudiante_id, seccion_id, periodo_id, fecha_matricula, estado) VALUES (%s, %s, %s, '2026-03-02', 'REGULAR')", (est_id, sec_id, periodo_id))
    mat_id = cursor.lastrowid
    
    estudiantes_mapeados.append((est_id, mat_id, p_id, sec_id))
    
    # Estructura de Ficha Médica asociada por alumno
    bulk_fichas.append((est_id, random.choice(tipos_sangre), random.choice(alergias_opc), 'Ninguna', f"Apoderado {ape}", generar_celular_peruano()))
    
    # Planificación de Pagos (Matrícula + 9 Mensualidades Escolares)
    bulk_pagos.append((mat_id, 'MATRICULA', None, 350.00, 350.00, '2026-03-02', '2026-03-02', 'PAGADO', 'EFECTIVO'))
    for mes in range(3, 12): # De Marzo a Noviembre
        monto = 300.00
        # Simulación de estados financieros según la fecha actual simulada
        if mes <= 6:
            bulk_pagos.append((mat_id, 'MENSUALIDAD', mes, monto, monto, f"2026-{mes:02d}-30", f"2026-{mes:02d}-28", 'PAGADO', 'TRANSFERENCIA'))
        elif mes == 7:
            bulk_pagos.append((mat_id, 'MENSUALIDAD', mes, monto, 0.00, f"2026-{mes:02d}-30", None, 'PENDIENTE', None))
        else:
            bulk_pagos.append((mat_id, 'MENSUALIDAD', mes, monto, 0.00, f"2026-{mes:02d}-30", None, 'PENDIENTE', None))

    # Extracción de Carga Académica de su sección para Calificaciones
    cursor.execute("SELECT curso_id FROM asignaciones_profesor WHERE seccion_id = %s", (sec_id,))
    cursos_en_aula = cursor.fetchall()
    for c_item in cursos_en_aula:
        for bimestre in range(1, 5):
            for t_eval in tipos_evaluacion:
                # INTEGRACIÓN: Distribución normal (Gauss con Media 14.5, Desviación 3.0) acotada
                nota_clon = random.gauss(14.5, 3.0)
                nota_valor = max(0.0, min(20.0, nota_clon))
                nota_valor = round(nota_valor, 2)
                
                bulk_notas.append((mat_id, c_item[0], bimestre, t_eval, nota_valor))

# Inserciones por lotes masivos de alto rendimiento
print("-> Impactando bloques de calificaciones, cobranza y fichas de salud...")
cursor.executemany("INSERT INTO fichas_medicas (estudiante_id, tipo_sangre, alergias, condiciones_cronicas, contacto_emergencia_nombre, contacto_emergencia_telefono) VALUES (%s, %s, %s, %s, %s, %s)", bulk_fichas)

BATCH_SIZE = 10000
for x in range(0, len(bulk_pagos), BATCH_SIZE):
    # CORRECCIÓN AQUÍ: Se cambió 'mes_corresponding' por el nombre correcto de columna 'mes_correspondiente'
    cursor.executemany("INSERT INTO pagos (matricula_id, concepto, mes_correspondiente, monto_total, monto_pagado, fecha_vencimiento, fecha_pago, estado, metodo_pago) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", bulk_pagos[x:x+BATCH_SIZE])
for x in range(0, len(bulk_notas), BATCH_SIZE):
    cursor.executemany("INSERT INTO notas (matricula_id, curso_id, bimestre, tipo_evaluacion, valor) VALUES (%s, %s, %s, %s, %s)", bulk_notas[x:x+BATCH_SIZE])
conn.commit()

# ==================================================
# 7. ASISTENCIAS DIARIAS EN CONDICIÓN TEMPORAL
# ==================================================
print("-> Replicando historial diario de asistencias (Marzo a Diciembre)...")
dias_laborables = []
fecha_curr = datetime.strptime('2026-03-02', '%Y-%m-%d').date()
fecha_limite = datetime.strptime('2026-12-18', '%Y-%m-%d').date()

while fecha_curr <= fecha_limite:
    if fecha_curr.weekday() < 5: # Lunes a Viernes
        dias_laborables.append(fecha_curr.strftime('%Y-%m-%d'))
    fecha_curr += timedelta(days=1)

obs_tarde = ["Tráfico en la avenida principal", "Inconveniente con la movilidad escolar", "Clima adverso", None]
obs_just = ["Atención médica programada", "Descanso médico por salud", "Asunto familiar de fuerza mayor"]

bulk_asistencias = []
for est_id, mat_id, p_id, sec_id in estudiantes_mapeados:
    for f_asist in dias_laborables:
        prob = random.random()
        if prob < 0.93:
            estado, obs = "PRESENTE", None
        elif prob < 0.97:
            estado, obs = "TARDE", random.choice(obs_tarde)
        elif prob < 0.99:
            estado, obs = "FALTA_INJUSTIFICADA", None
        else:
            estado, obs = "FALTA_JUSTIFICADA", random.choice(obs_just)
            
        bulk_asistencias.append((mat_id, f_asist, estado, obs))
        
        if len(bulk_asistencias) >= BATCH_SIZE:
            cursor.executemany("INSERT INTO asistencias_estudiantes (matricula_id, fecha, estado, observaciones) VALUES (%s, %s, %s, %s)", bulk_asistencias)
            bulk_asistencias.clear()
if bulk_asistencias:
    cursor.executemany("INSERT INTO asistencias_estudiantes (matricula_id, fecha, estado, observaciones) VALUES (%s, %s, %s, %s)", bulk_asistencias)
conn.commit()

# ==================================================
# 8. POBLADO TRANSACCIONAL DE INCIDENCIAS (ENFERMERÍA, CONDUCTA Y BIBLIOTECA)
# ==================================================
print("-> Completando reportes disciplinarios, atenciones de salud y préstamos...")
sanciones_dict = {
    'LEVE': ('Llamado de atención verbal en aula', 'Uso inadecuado del uniforme escolar'),
    'MODERADA': ('Citación formal al padre de familia', 'Infracción reiterada a las normas de convivencia'),
    'GRAVE': ('Suspensión interna de actividades por 1 día', 'Falta de respeto grave a un docente'),
    'MUY GRAVE': ('Suspensión académica de 3 días con cargo', 'Daño intencional a la infraestructura tecnológica')
}

# Elegimos una muestra aleatoria para registrar eventos específicos e impedir tablas vacías
alumnos_incidentes = random.sample(estudiantes_mapeados, 300)
for est_id, mat_id, p_id, sec_id in alumnos_incidentes:
    # 1. Atenciones Médicas
    cursor.execute("INSERT INTO atenciones_enfermeria (estudiante_id, sintomas, tratamiento_aplicado, deriva_hospital) VALUES (%s, 'Cefalea y dolor estomacal leve', 'Administración de analgésico autorizado y descanso en camilla', 0)", (est_id,))
    
    # 2. Conducta
    grav = random.choice(['LEVE', 'MODERADA', 'GRAVE', 'MUY GRAVE'])
    sancion, desc = sanciones_dict[grav]
    cursor.execute("SELECT profesor_id FROM asignaciones_profesor WHERE seccion_id = %s LIMIT 1", (sec_id,))
    prof_reporta = cursor.fetchone()[0]
    cursor.execute("INSERT INTO reportes_disciplinarios (estudiante_id, profesor_reporta_id, fecha_incidente, gravedad, descripcion, sancion_aplicada) VALUES (%s, %s, '2026-05-18', %s, %s, %s)", (est_id, prof_reporta, grav, desc, sancion))
    
    # 3. Biblioteca
    lib_id = random.choice(libros_ids)
    cursor.execute("INSERT INTO prestamos_biblioteca (libro_id, persona_id, fecha_prestamo, fecha_devolucion_esperada, fecha_devolucion_real, estado) VALUES (%s, %s, '2026-04-10', '2026-04-17', '2026-04-16', 'DEVUELTO')", (lib_id, p_id))

# Liquidación de transacciones pendientes y cierre seguro
conn.commit()
print("==================================================")
print("¡PROCESO COMPLETADO EXITOSAMENTE!")
print("-> Absolutamente todas las tablas cuentan con data íntegra.")
print("==================================================")

cursor.close()
conn.close()