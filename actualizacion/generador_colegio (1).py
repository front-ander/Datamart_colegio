import random
import pymysql
import re
from datetime import datetime, timedelta

# ==================================================
# 1. CONFIGURACIÓN Y CONSTANTES
# ==================================================

# Rangos de edad por nivel educativo (edades realistas)
RANGOS_EDAD = {
    'PRIMARIA': {
        1: (6, 7),
        2: (7, 8),
        3: (8, 9),
        4: (9, 10),
        5: (10, 11),
        6: (11, 12)
    },
    'SECUNDARIA': {
        1: (12, 13),
        2: (13, 14),
        3: (14, 15),
        4: (15, 16),
        5: (16, 17)
    }
}

# Nombres más comunes en Perú
NOMBRES_HOMBRES = [
    'Kevin', 'Carlos', 'Luis', 'Juan', 'Jorge', 'Pedro', 'Miguel', 'Angel',
    'Diego', 'Alejandro', 'José', 'Christian', 'Manuel', 'Ricardo', 'Fernando',
    'David', 'Santiago', 'Sebastián', 'Mateo', 'Gabriel', 'Lucas', 'Daniel',
    'Eduardo', 'Alonso', 'Rodrigo', 'Gonzalo', 'Mauricio', 'Javier', 'Arturo',
    'Enrique', 'César', 'Iván', 'Gustavo', 'Héctor', 'Fabrizio', 'Renato',
    'Josué', 'Samuel', 'Alexander', 'Aaron', 'Anthony', 'Jean', 'Bryan',
    'Leonardo', 'Matías', 'Álvaro', 'Andrés', 'Hugo', 'Marcos', 'Víctor',
    'Raúl', 'Oscar', 'Pablo', 'Felipe', 'Joaquín', 'Emilio', 'Adrián'
]

NOMBRES_MUJERES = [
    'Camila', 'María', 'Ana', 'Lucía', 'Sofía', 'Laura', 'Elena', 'Gabriela',
    'Valeria', 'Claudia', 'Paola', 'Andrea', 'Milagros', 'Fiorella', 'Natalia',
    'Daniela', 'Isabella', 'Valentina', 'Alejandra', 'Diana', 'Beatriz', 'Ximena',
    'Adriana', 'Luciana', 'Fernanda', 'Carolina', 'Mariana', 'Vanessa', 'Jessica',
    'Karla', 'Cecilia', 'Roxana', 'Liliana', 'Patricia', 'Rosa', 'Carmen',
    'Elizabeth', 'Angélica', 'Nicole', 'Melany', 'Estefany', 'Kiara', 'Bianca',
    'Giselle', 'Valerie', 'Camille', 'Alessandra', 'Fabiola', 'Tatiana', 'Ariadna',
    'Jimena', 'Regina', 'Micaela', 'Alondra', 'Alessia', 'Aitana', 'Chloe'
]

APELLIDOS_PERUANOS = [
    'García', 'Mendoza', 'Rodríguez', 'López', 'Martínez', 'Pérez', 'Gómez',
    'Sánchez', 'Díaz', 'Torres', 'Ramírez', 'Flores', 'Castro', 'Romero',
    'Quispe', 'Gonzales', 'Chávez', 'Espinoza', 'Ramos', 'Fernández', 'Silva',
    'Rojas', 'Herrera', 'Palomino', 'Gutiérrez', 'Vargas', 'Vásquez', 'Castillo',
    'Yarlequé', 'Sullón', 'Vilchez', 'Sandoval', 'Farfán', 'Campos', 'Guerrero',
    'Zapata', 'Agurto', 'Garrido', 'Saavedra', 'Correa', 'Moreno', 'Pacherres',
    'Panta', 'Navarro', 'Salinas', 'Pingo', 'Seminario', 'Olaya', 'Juárez',
    'Huamán', 'Soto', 'Mamani', 'Condori', 'Aguilar', 'Cruz', 'Morales'
]

# Conjuntos para evitar duplicados
dnis_generados = set()
correos_generados = set()
usernames_generados = set()
codigos_estudiantes_generados = set()

# ==================================================
# 2. CONEXIÓN A LA BASE DE DATOS
# ==================================================

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    database='ccole',
    autocommit=False
)
cursor = conn.cursor()

print("==================================================")
print("INICIANDO GENERACIÓN DE DATA REALISTA (OLTP 2024-2026)")
print("==================================================")

# ==================================================
# 3. FUNCIONES AUXILIARES
# ==================================================

def generar_dni_peruano():
    """Genera DNI peruano válido (8 dígitos)"""
    while True:
        dni = f"{random.randint(10000000, 99999999)}"
        if dni not in dnis_generados:
            dnis_generados.add(dni)
            return dni

def generar_celular_peruano():
    """Genera número de celular peruano válido (9 dígitos empezando con 9)"""
    return f"9{random.randint(10000000, 99999999)}"

def limpiar_texto(texto):
    """Limpia texto para usar en correos/usuarios"""
    texto = texto.lower().strip()
    texto = re.sub(r'[áàäâ]', 'a', texto)
    texto = re.sub(r'[éèëê]', 'e', texto)
    texto = re.sub(r'[íìïî]', 'i', texto)
    texto = re.sub(r'[óòöô]', 'o', texto)
    texto = re.sub(r'[úùüû]', 'u', texto)
    texto = re.sub(r'[ñ]', 'n', texto)
    return re.sub(r'[^a-z0-9]', '', texto)

def generar_correo_realista(nombre, apellido, dominio="colegio.edu.pe"):
    """Genera correo electrónico realista"""
    primer_nom = limpiar_texto(nombre.split()[0])
    primer_ape = limpiar_texto(apellido.split()[0])
    
    formatos = [
        f"{primer_nom}.{primer_ape}@{dominio}",
        f"{primer_nom}{primer_ape}@{dominio}",
        f"{primer_nom}_{primer_ape}@{dominio}",
        f"{primer_ape}.{primer_nom}@{dominio}",
        f"{primer_nom[0]}{primer_ape}@{dominio}",
        f"{primer_nom}.{primer_ape[0]}@{dominio}"
    ]
    
    correo = random.choice(formatos)
    contador = 1
    while correo in correos_generados:
        if contador > 1:
            correo = correo.replace(f"@{dominio}", f"{contador}@{dominio}")
        else:
            base = correo.split('@')[0]
            correo = f"{base}{random.randint(1,99)}@{dominio}"
        contador += 1
    
    correos_generados.add(correo)
    return correo

def crear_usuario_realista(nombre, apellido, rol):
    """Crea usuario con credenciales realistas"""
    p_nom = limpiar_texto(nombre.split()[0])
    p_ape = limpiar_texto(apellido.split()[0])
    
    username = f"{p_nom}.{p_ape}"
    contador = 1
    while username in usernames_generados:
        username = f"{p_nom}.{p_ape}{contador}"
        contador += 1
    usernames_generados.add(username)
    
    pwd_hash = "$2y$10$" + "".join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789./', k=53))
    
    cursor.execute("""
        INSERT INTO usuarios (username, password_hash, rol_id, estado) 
        VALUES (%s, %s, %s, 'ACTIVO')
    """, (username, pwd_hash, rol))
    return cursor.lastrowid

def generar_direccion_piura():
    """Genera una dirección realista de Piura"""
    calles = [
        'Av. Grau', 'Av. Sánchez Cerro', 'Calle Lima', 'Jr. Ayacucho',
        'Av. Los Cocos', 'Calle La Merced', 'Jr. Cuzco', 'Av. Andrés Avelino Cáceres',
        'Calle San Miguel', 'Av. Progreso', 'Jr. Libertad', 'Calle Arequipa',
        'Av. Los Algarrobos', 'Calle Tacna', 'Jr. Piura', 'Av. Circunvalación',
        'Calle Los Ángeles', 'Av. La Paz', 'Jr. Cajamarca', 'Calle Grau',
        'Av. Ramón Castilla', 'Calle Los Olivos', 'Jr. Ica', 'Av. Tumbes',
        'Calle San Francisco', 'Av. Los Incas', 'Jr. Huancavelica', 'Calle Puno',
        'Av. El Bosque', 'Calle Los Rosales', 'Jr. Áncash', 'Av. Chulucanas'
    ]
    
    urbanizaciones = [
        'Urb. Miraflores', 'Urb. San Eduardo', 'Urb. Los Algarrobos',
        'Urb. Santa Isabel', 'Urb. Los Ejidos', 'Urb. Ignacio Merino',
        'Urb. San José', 'Urb. Los Fresnos', 'Urb. El Bosque',
        'Urb. La Primavera', 'Urb. Los Ángeles', 'Urb. San Martín'
    ]
    
    distritos_piura = [
        'Piura', 'Castilla', 'Veintiséis de Octubre', 'Catacaos',
        'La Unión', 'Los Ejidos', 'Tambogrande', 'Sullana'
    ]
    
    formatos = [
        f"{random.choice(calles)} {random.randint(100, 999)} - {random.choice(distritos_piura)}",
        f"{random.choice(calles)} {random.randint(100, 999)} - {random.choice(urbanizaciones)} - {random.choice(distritos_piura)}",
        f"{random.choice(calles)} {random.randint(100, 999)} - {random.choice(distritos_piura)} - {random.choice(distritos_piura)}"
    ]
    
    return random.choice(formatos)

def generar_fecha_aleatoria(anio, mes_min=1, mes_max=12, dia_min=1, dia_max=28):
    """Genera una fecha aleatoria dentro de un rango"""
    mes = random.randint(mes_min, mes_max)
    dia = random.randint(dia_min, dia_max)
    return datetime(anio, mes, dia)

def generar_codigo_estudiante_unico(anio):
    """Genera un código de estudiante único"""
    while True:
        codigo = f"EST-{anio}-{random.randint(10000, 99999)}"
        if codigo not in codigos_estudiantes_generados:
            codigos_estudiantes_generados.add(codigo)
            return codigo

# ==================================================
# 4. LIMPIEZA DE DATOS PREVIOS
# ==================================================

print("-> Limpiando datos existentes...")
cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
tablas = [
    'prestamos_biblioteca', 'libros', 'inventario_equipos', 'fichas_medicas',
    'atenciones_enfermeria', 'reportes_disciplinarios', 'pagos', 'notas',
    'asistencias_estudiantes', 'asignaciones_profesor', 'matriculas',
    'estudiantes', 'profesores', 'personas', 'usuarios', 'roles',
    'secciones', 'grados', 'cursos', 'periodos_academicos'
]
for tabla in tablas:
    cursor.execute(f"DELETE FROM `{tabla}`;")
    cursor.execute(f"ALTER TABLE `{tabla}` AUTO_INCREMENT = 1;")
cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
conn.commit()

# ==================================================
# 5. CATÁLOGOS Y ESTRUCTURA BASE
# ==================================================

print("-> Configurando catálogos base...")

# Roles
cursor.execute("INSERT INTO roles (nombre) VALUES ('ADMIN'), ('DOCENTE'), ('ESTUDIANTE')")
cursor.execute("SELECT id, nombre FROM roles")
mapa_roles = {row[1]: row[0] for row in cursor.fetchall()}

# Periodos académicos (2024-2026)
periodos = []
for anio in [2024, 2025, 2026]:
    cursor.execute("""
        INSERT INTO periodos_academicos (anio, fecha_inicio, fecha_fin, estado) 
        VALUES (%s, %s, %s, 'ACTIVO')
    """, (anio, datetime(anio, 3, 2), datetime(anio, 12, 18)))
    periodos.append(cursor.lastrowid)

# Grados
grados_map = {}
for nivel in ['PRIMARIA', 'SECUNDARIA']:
    max_grado = 6 if nivel == 'PRIMARIA' else 5
    for g in range(1, max_grado + 1):
        nombre = f"{g}° {nivel}"
        cursor.execute("INSERT INTO grados (nombre, nivel) VALUES (%s, %s)", (nombre, nivel))
        grado_id = cursor.lastrowid
        grados_map[(nivel, g)] = grado_id

# Secciones (A, B, C por grado)
secciones_map = {}
for (nivel, grado), grado_id in grados_map.items():
    for letra in ['A', 'B', 'C']:
        cursor.execute("""
            INSERT INTO secciones (grado_id, letra, turno) 
            VALUES (%s, %s, 'MAÑANA')
        """, (grado_id, letra))
        seccion_id = cursor.lastrowid
        secciones_map[(nivel, grado, letra)] = seccion_id

# Cursos
cursos_primaria = [
    ('Matemática', 'CIENCIAS'),
    ('Comunicación', 'LETRAS'),
    ('Ciencia y Ambiente', 'CIENCIAS'),
    ('Personal Social', 'LETRAS'),
    ('Religión', 'LETRAS'),
    ('Computación', 'TECNOLOGÍA'),
    ('Arte', 'ARTE'),
    ('Educación Física', 'DEPORTE'),
    ('Inglés', 'IDIOMAS'),
    ('Tutoría', 'OTROS')
]

cursos_secundaria = [
    ('Matemática', 'CIENCIAS'),
    ('Comunicación', 'LETRAS'),
    ('Física', 'CIENCIAS'),
    ('Química', 'CIENCIAS'),
    ('Biología', 'CIENCIAS'),
    ('Historia y Geografía', 'LETRAS'),
    ('Religión', 'LETRAS'),
    ('Computación', 'TECNOLOGÍA'),
    ('Arte', 'ARTE'),
    ('Educación Física', 'DEPORTE'),
    ('Inglés', 'IDIOMAS'),
    ('Tutoría', 'OTROS')
]

cursos_map = {}
for nombre, area in cursos_primaria + cursos_secundaria:
    cursor.execute("INSERT INTO cursos (nombre, area) VALUES (%s, %s)", (nombre, area))
    cursos_map[nombre] = cursor.lastrowid

conn.commit()

# ==================================================
# 6. GENERACIÓN DE PROFESORES
# ==================================================

print("-> Generando profesores...")

profesores_primaria = []
profesores_secundaria = []

def crear_profesor(genero, especialidad):
    """Crea un profesor con datos realistas"""
    nombres_list = NOMBRES_HOMBRES if genero == 'H' else NOMBRES_MUJERES
    nombre = random.choice(nombres_list)
    nombre2 = random.choice(nombres_list)
    apellido1 = random.choice(APELLIDOS_PERUANOS)
    apellido2 = random.choice(APELLIDOS_PERUANOS)
    apellidos = f"{apellido1} {apellido2}"
    
    anio_nac = random.randint(1960, 1995)
    fecha_nac = generar_fecha_aleatoria(anio_nac)
    
    usuario_id = crear_usuario_realista(nombre, apellidos, mapa_roles['DOCENTE'])
    
    dni = generar_dni_peruano()
    telefono = generar_celular_peruano()
    correo = generar_correo_realista(nombre, apellidos, "colegio.edu.pe")
    direccion = generar_direccion_piura()
    
    cursor.execute("""
        INSERT INTO personas (usuario_id, dni, nombres, apellidos, fecha_nacimiento, 
                            direccion, telefono, email) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (usuario_id, dni, f"{nombre} {nombre2}", apellidos, 
          fecha_nac, direccion, telefono, correo))
    persona_id = cursor.lastrowid
    
    codigo = f"PROF-{random.randint(1000, 9999)}"
    cursor.execute("""
        INSERT INTO profesores (persona_id, codigo_profesor, especialidad) 
        VALUES (%s, %s, %s)
    """, (persona_id, codigo, especialidad))
    
    return cursor.lastrowid

# Crear profesores
especialidades_primaria = [
    'Lic. Educación Primaria - Matemática',
    'Lic. Educación Primaria - Comunicación',
    'Lic. Educación Primaria - Ciencias',
    'Lic. Educación Primaria - Sociales',
    'Lic. Educación Primaria - Arte',
    'Lic. Educación Primaria - Educación Física',
    'Lic. Educación Primaria - Computación',
    'Lic. Educación Primaria - Inglés',
    'Lic. Educación Primaria - Tutoría'
]

especialidades_secundaria = [
    'Lic. Matemática - Secundaria',
    'Lic. Comunicación - Secundaria',
    'Lic. Física - Secundaria',
    'Lic. Química - Secundaria',
    'Lic. Biología - Secundaria',
    'Lic. Historia - Secundaria',
    'Lic. Religión - Secundaria',
    'Lic. Computación - Secundaria',
    'Lic. Arte - Secundaria',
    'Lic. Educación Física - Secundaria',
    'Lic. Inglés - Secundaria',
    'Lic. Tutoría - Secundaria'
]

profesores = {}
for especialidad in especialidades_primaria:
    profesor_id = crear_profesor(random.choice(['H', 'M']), especialidad)
    profesores[especialidad] = profesor_id
    profesores_primaria.append(profesor_id)

for especialidad in especialidades_secundaria:
    profesor_id = crear_profesor(random.choice(['H', 'M']), especialidad)
    profesores[especialidad] = profesor_id
    profesores_secundaria.append(profesor_id)

# Asignar tutores
print("-> Asignando tutores a secciones...")
for (nivel, grado, letra), seccion_id in secciones_map.items():
    tutor_especialidad = 'Lic. Educación Primaria - Tutoría' if nivel == 'PRIMARIA' else 'Lic. Tutoría - Secundaria'
    curso_tutoria = cursos_map['Tutoría']
    profesor_tutor = profesores[tutor_especialidad]
    
    for periodo_id in periodos:
        cursor.execute("""
            INSERT INTO asignaciones_profesor (profesor_id, curso_id, seccion_id, periodo_id) 
            VALUES (%s, %s, %s, %s)
        """, (profesor_tutor, curso_tutoria, seccion_id, periodo_id))

# Asignar profesores a cursos
print("-> Asignando cursos a profesores...")
for (nivel, grado, letra), seccion_id in secciones_map.items():
    if nivel == 'PRIMARIA':
        cursos_nivel = ['Matemática', 'Comunicación', 'Ciencia y Ambiente', 'Personal Social', 
                       'Religión', 'Computación', 'Arte', 'Educación Física', 'Inglés']
    else:
        cursos_nivel = ['Matemática', 'Comunicación', 'Física', 'Química', 'Biología', 
                       'Historia y Geografía', 'Religión', 'Computación', 'Arte', 
                       'Educación Física', 'Inglés']
    
    for curso_nombre in cursos_nivel:
        curso_id = cursos_map[curso_nombre]
        
        profesor_id = None
        for esp, prof_id in profesores.items():
            if curso_nombre in esp:
                profesor_id = prof_id
                break
        
        if not profesor_id:
            profesor_id = random.choice(profesores_primaria if nivel == 'PRIMARIA' else profesores_secundaria)
        
        for periodo_id in periodos:
            cursor.execute("""
                INSERT INTO asignaciones_profesor (profesor_id, curso_id, seccion_id, periodo_id) 
                VALUES (%s, %s, %s, %s)
            """, (profesor_id, curso_id, seccion_id, periodo_id))

conn.commit()

# ==================================================
# 7. GENERACIÓN DE LIBROS Y EQUIPOS
# ==================================================

print("-> Generando catálogo de biblioteca...")
libros_biblioteca = [
    ('9786123164123', 'Álgebra de Baldor', 'Aurelio Baldor', 'Matemáticas', 25),
    ('9788420655659', 'Don Quijote de la Mancha', 'Miguel de Cervantes', 'Literatura', 30),
    ('9786124256112', 'Tradiciones Peruanas', 'Ricardo Palma', 'Historia', 20),
    ('9789501245630', 'Pedagogía del Oprimido', 'Paulo Freire', 'Educación', 5),
    ('9786123172029', 'Física Universitaria', 'Sears Zemansky', 'Física', 15),
    ('9788420635491', 'Cien años de soledad', 'Gabriel García Márquez', 'Literatura', 40),
    ('9786123171817', 'Química General', 'Raymond Chang', 'Química', 12),
    ('9788420655284', 'El Principito', 'Antoine de Saint-Exupéry', 'Literatura', 35),
    ('9786124256365', 'Historia del Perú', 'José Antonio del Busto', 'Historia', 18),
    ('9789501238526', 'Matemáticas Simplificadas', 'Conamat', 'Matemáticas', 22)
]

libros_data = [(isbn, titulo, autor, categoria, stock, stock) for isbn, titulo, autor, categoria, stock in libros_biblioteca]
cursor.executemany("""
    INSERT INTO libros (codigo_isbn, titulo, autor, categoria, stock_total, stock_disponible) 
    VALUES (%s, %s, %s, %s, %s, %s)
""", libros_data)

# Equipos
print("-> Generando inventario de equipos...")
equipos_categorias = [
    ('Proyector Epson', 'TECNOLOGÍA'),
    ('Laptop Dell', 'TECNOLOGÍA'),
    ('Pizarra Digital', 'TECNOLOGÍA'),
    ('Computadora HP', 'TECNOLOGÍA'),
    ('Tablet iPad', 'TECNOLOGÍA'),
    ('Impresora', 'TECNOLOGÍA'),
    ('Equipo de Sonido', 'TECNOLOGÍA'),
    ('Televisor LED', 'TECNOLOGÍA'),
    ('Router WiFi', 'TECNOLOGÍA'),
    ('Cámara de Video', 'TECNOLOGÍA')
]

codigos_inventario = set()
for (nivel, grado, letra), seccion_id in secciones_map.items():
    for _ in range(random.randint(2, 4)):
        equipo, categoria = random.choice(equipos_categorias)
        while True:
            codigo = f"PAT-{random.randint(2024,2026)}-{random.randint(1000,9999)}"
            if codigo not in codigos_inventario:
                codigos_inventario.add(codigo)
                break
        descripcion = f"{equipo} - Aula {grado} {nivel} {letra}"
        
        anio_adq = random.randint(2020, 2026)
        fecha_adq = generar_fecha_aleatoria(anio_adq)
        
        valor = round(random.uniform(500, 5000), 2)
        estado = random.choices(['NUEVO', 'BUENO', 'REGULAR', 'MALOGRADO'], weights=[0.2, 0.5, 0.2, 0.1])[0]
        
        cursor.execute("""
            INSERT INTO inventario_equipos (codigo_patrimonial, categoria, descripcion, 
                                           estado, fecha_adquisicion, valor_adquisicion, ubicacion) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (codigo, categoria, descripcion, estado, fecha_adq, valor, f"Aula {grado}° {nivel} {letra}"))

conn.commit()

# ==================================================
# 8. GENERACIÓN DE ESTUDIANTES (CON REPITENTES DISCRETOS)
# ==================================================

print("-> Generando estudiantes...")

cursor.execute("""
    SELECT s.id, g.nombre, g.nivel, s.letra 
    FROM secciones s 
    JOIN grados g ON s.grado_id = g.id
""")
secciones_info = cursor.fetchall()

all_estudiantes = []

# Diccionario para rastrear estudiantes de años anteriores (para repitencias)
estudiantes_previos = []

for periodo_idx, periodo_id in enumerate(periodos):
    anio = 2024 + periodo_idx
    print(f"  Generando estudiantes para {anio}...")
    
    # Lista de IDs de estudiantes que repiten este año
    repitentes_ids = set()
    
    # Si no es el primer año, seleccionar algunos estudiantes que repiten (discreto)
    if anio > 2024 and len(estudiantes_previos) > 0:
        # Seleccionar entre 10-15 estudiantes para que repitan (1-2% del total)
        num_repitentes = random.randint(10, 15)
        num_repitentes = min(num_repitentes, len(estudiantes_previos))
        
        if num_repitentes > 0:
            # Seleccionar estudiantes aleatorios para que repitan
            estudiantes_seleccionados = random.sample(estudiantes_previos, num_repitentes)
            
            # Crear nuevas matrículas para los repitentes
            for est_prev in estudiantes_seleccionados:
                estudiante_id = est_prev['estudiante_id']
                persona_id = est_prev['persona_id']
                
                # Asignar a una sección del mismo grado o similar
                grado_anterior = est_prev['grado']
                nivel_anterior = est_prev['nivel']
                
                # Buscar secciones del mismo grado
                secciones_mismo_grado = [s for s in secciones_info if s[1] == f"{grado_anterior}° {nivel_anterior}"]
                if secciones_mismo_grado:
                    sec_asignada = random.choice(secciones_mismo_grado)[0]
                else:
                    # Si no hay, usar la sección original
                    sec_asignada = est_prev['seccion_id']
                
                dia_matricula = random.randint(1, 15)
                fecha_matricula = datetime(anio, 3, dia_matricula)
                
                cursor.execute("""
                    INSERT INTO matriculas (estudiante_id, periodo_id, seccion_id, 
                                          fecha_matricula, estado) 
                    VALUES (%s, %s, %s, %s, 'REGULAR')
                """, (estudiante_id, periodo_id, sec_asignada, fecha_matricula))
                matricula_id = cursor.lastrowid
                
                # Registrar como repitente
                repitentes_ids.add(estudiante_id)
                
                # Añadir a la lista de estudiantes del año actual
                estudiante_info = {
                    'estudiante_id': estudiante_id,
                    'persona_id': persona_id,
                    'matricula_id': matricula_id,
                    'seccion_id': sec_asignada,
                    'periodo_id': periodo_id,
                    'anio': anio,
                    'grado': grado_anterior,
                    'nivel': nivel_anterior,
                    'es_repitente': True
                }
                all_estudiantes.append(estudiante_info)
    
    # Generar estudiantes nuevos
    for seccion in secciones_info:
        seccion_id, grado_nombre, nivel, letra = seccion
        grado_num = int(grado_nombre.split('°')[0])
        
        if nivel == 'PRIMARIA':
            edad_min, edad_max = RANGOS_EDAD['PRIMARIA'][grado_num]
        else:
            edad_min, edad_max = RANGOS_EDAD['SECUNDARIA'][grado_num]
        
        # Número de estudiantes en esta sección (considerando repitentes ya asignados)
        repitentes_en_seccion = sum(1 for e in all_estudiantes 
                                   if e.get('seccion_id') == seccion_id 
                                   and e.get('anio') == anio 
                                   and e.get('es_repitente', False))
        
        num_estudiantes = random.randint(24, 28)
        # Ajustar para no exceder el rango
        estudiantes_nuevos = max(0, num_estudiantes - repitentes_en_seccion)
        
        for i in range(estudiantes_nuevos):
            genero = random.choice(['H', 'M'])
            nombres_list = NOMBRES_HOMBRES if genero == 'H' else NOMBRES_MUJERES
            
            nombre = random.choice(nombres_list)
            nombre2 = random.choice(nombres_list)
            apellido1 = random.choice(APELLIDOS_PERUANOS)
            apellido2 = random.choice(APELLIDOS_PERUANOS)
            apellidos = f"{apellido1} {apellido2}"
            
            anio_nacimiento = anio - random.randint(edad_min, edad_max)
            fecha_nac = generar_fecha_aleatoria(anio_nacimiento)
            
            usuario_id = crear_usuario_realista(nombre, apellidos, mapa_roles['ESTUDIANTE'])
            
            dni = generar_dni_peruano()
            telefono = generar_celular_peruano()
            correo = generar_correo_realista(nombre, apellidos, "est.colegio.edu.pe")
            direccion = generar_direccion_piura()
            
            cursor.execute("""
                INSERT INTO personas (usuario_id, dni, nombres, apellidos, fecha_nacimiento, 
                                    direccion, telefono, email) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (usuario_id, dni, f"{nombre} {nombre2}", apellidos, 
                  fecha_nac, direccion, telefono, correo))
            persona_id = cursor.lastrowid
            
            codigo_est = generar_codigo_estudiante_unico(anio)
            fecha_ingreso = datetime(anio, 3, 2)
            
            cursor.execute("""
                INSERT INTO estudiantes (persona_id, codigo_estudiante, fecha_ingreso) 
                VALUES (%s, %s, %s)
            """, (persona_id, codigo_est, fecha_ingreso))
            estudiante_id = cursor.lastrowid
            
            dia_matricula = random.randint(1, 15)
            fecha_matricula = datetime(anio, 3, dia_matricula)
            
            cursor.execute("""
                INSERT INTO matriculas (estudiante_id, periodo_id, seccion_id, 
                                      fecha_matricula, estado) 
                VALUES (%s, %s, %s, %s, 'REGULAR')
            """, (estudiante_id, periodo_id, seccion_id, fecha_matricula))
            matricula_id = cursor.lastrowid
            
            estudiante_info = {
                'estudiante_id': estudiante_id,
                'persona_id': persona_id,
                'matricula_id': matricula_id,
                'seccion_id': seccion_id,
                'periodo_id': periodo_id,
                'anio': anio,
                'grado': grado_num,
                'nivel': nivel,
                'fecha_nacimiento': fecha_nac,
                'apellidos': apellidos,
                'nombre_completo': f"{nombre} {nombre2} {apellidos}",
                'es_repitente': False
            }
            
            all_estudiantes.append(estudiante_info)
    
    # Guardar estudiantes de este año para posibles repitencias futuras
    estudiantes_previos = [e for e in all_estudiantes if e.get('anio') == anio and not e.get('es_repitente', False)]

conn.commit()
print(f"  Total estudiantes generados: {len(all_estudiantes)}")

# ==================================================
# 9. GENERACIÓN DE NOTAS (CON NOTAS MÁS BAJAS PARA REPITENTES)
# ==================================================

print("-> Generando calificaciones...")

tipos_evaluacion = ['EXAMEN_PARCIAL', 'EXAMEN_FINAL', 'PRACTICA', 'TAREA']
bulk_notas = []
total_notas = 0

# Mapa rápido de estudiantes repitentes
es_repitente_map = {e['estudiante_id']: True for e in all_estudiantes if e.get('es_repitente', False)}

for estudiante in all_estudiantes:
    matricula_id = estudiante['matricula_id']
    seccion_id = estudiante['seccion_id']
    periodo_id = estudiante['periodo_id']
    es_repitente = es_repitente_map.get(estudiante['estudiante_id'], False)
    
    cursor.execute("""
        SELECT curso_id FROM asignaciones_profesor 
        WHERE seccion_id = %s AND periodo_id = %s
    """, (seccion_id, periodo_id))
    cursos = cursor.fetchall()
    
    for curso in cursos:
        curso_id = curso[0]
        
        for bimestre in range(1, 5):
            for tipo_eval in tipos_evaluacion:
                if es_repitente:
                    # Notas mucho más bajas para repitentes
                    if random.random() < 0.7:
                        media = random.uniform(4, 9)
                    else:
                        media = random.uniform(9, 13)
                else:
                    # Distribución normal para estudiantes regulares
                    if random.random() < 0.1:
                        media = random.uniform(8, 11)
                    elif random.random() < 0.15:
                        media = random.uniform(17, 19.5)
                    else:
                        media = random.uniform(11, 17)
                
                sigma = random.uniform(1.5, 3.5)
                nota = random.gauss(media, sigma)
                nota = max(0, min(20, nota))
                nota = round(nota, 2)
                
                bulk_notas.append((matricula_id, curso_id, bimestre, tipo_eval, nota))
                total_notas += 1
                
                if len(bulk_notas) >= 10000:
                    cursor.executemany("""
                        INSERT INTO notas (matricula_id, curso_id, bimestre, 
                                         tipo_evaluacion, valor) 
                        VALUES (%s, %s, %s, %s, %s)
                    """, bulk_notas)
                    conn.commit()
                    bulk_notas = []

if bulk_notas:
    cursor.executemany("""
        INSERT INTO notas (matricula_id, curso_id, bimestre, 
                         tipo_evaluacion, valor) 
        VALUES (%s, %s, %s, %s, %s)
    """, bulk_notas)
    conn.commit()

print(f"  Total calificaciones generadas: {total_notas}")

# ==================================================
# 10. GENERACIÓN DE ASISTENCIAS (CON MÁS FALTAS PARA REPITENTES)
# ==================================================

print("-> Generando asistencias...")

def generar_asistencias_por_estudiante(matricula_id, anio, es_repitente=False):
    asistencias = []
    inicio = datetime(anio, 3, 2)
    fin = datetime(anio, 12, 18)
    
    fecha = inicio
    while fecha <= fin:
        if fecha.weekday() < 5:
            if es_repitente:
                prob_presente = 0.72
            else:
                prob_presente = 0.92
            
            if fecha.month in [6, 7, 12]:
                prob_presente -= 0.05
            elif fecha.month == 4:
                prob_presente -= 0.03
            
            if fecha.weekday() in [0, 4]:
                prob_presente -= 0.03
            
            rand = random.random()
            if rand < prob_presente:
                estado = 'PRESENTE'
                observacion = None
            elif rand < prob_presente + 0.04:
                estado = 'TARDE'
                observaciones_tarde = ["Tráfico", "Lluvia", "Problemas de transporte", "Llegó tarde"]
                observacion = random.choice(observaciones_tarde)
            elif rand < prob_presente + 0.06:
                estado = 'FALTA_INJUSTIFICADA'
                observacion = None
            else:
                estado = 'FALTA_JUSTIFICADA'
                observaciones_just = ["Atención médica", "Trámite personal", "Enfermedad", "Emergencia familiar"]
                observacion = random.choice(observaciones_just)
            
            asistencias.append((matricula_id, fecha.strftime('%Y-%m-%d'), estado, observacion))
        
        fecha += timedelta(days=1)
    
    return asistencias

bulk_asistencias = []
total_asistencias = 0

for estudiante in all_estudiantes:
    es_repitente = es_repitente_map.get(estudiante['estudiante_id'], False)
    asistencias = generar_asistencias_por_estudiante(
        estudiante['matricula_id'],
        estudiante['anio'],
        es_repitente
    )
    bulk_asistencias.extend(asistencias)
    total_asistencias += len(asistencias)
    
    if len(bulk_asistencias) >= 10000:
        cursor.executemany("""
            INSERT INTO asistencias_estudiantes (matricula_id, fecha, estado, observaciones) 
            VALUES (%s, %s, %s, %s)
        """, bulk_asistencias)
        conn.commit()
        bulk_asistencias = []

if bulk_asistencias:
    cursor.executemany("""
        INSERT INTO asistencias_estudiantes (matricula_id, fecha, estado, observaciones) 
        VALUES (%s, %s, %s, %s)
    """, bulk_asistencias)
    conn.commit()

print(f"  Total asistencias generadas: {total_asistencias}")

# ==================================================
# 11. GENERACIÓN DE PAGOS (CON MÁS MOROSIDAD PARA REPITENTES)
# ==================================================

print("-> Generando pagos y finanzas...")

bulk_pagos = []
total_pagos = 0

for estudiante in all_estudiantes:
    matricula_id = estudiante['matricula_id']
    anio = estudiante['anio']
    es_repitente = es_repitente_map.get(estudiante['estudiante_id'], False)
    
    # Pago de matrícula
    dia_matricula = random.randint(1, 15)
    fecha_matricula = datetime(anio, 3, dia_matricula)
    
    monto_matricula = round(random.uniform(250, 400), 2)
    bulk_pagos.append((
        matricula_id, 'MATRICULA', None, monto_matricula, monto_matricula,
        fecha_matricula, fecha_matricula, 'PAGADO', random.choice(['EFECTIVO', 'TRANSFERENCIA'])
    ))
    total_pagos += 1
    
    # Mensualidades
    for mes in range(3, 12):
        monto_mensual = round(random.uniform(280, 350), 2)
        fecha_vencimiento = datetime(anio, mes, 30)
        
        if es_repitente:
            if mes <= 6:
                prob_pago = 0.50
            elif mes <= 9:
                prob_pago = 0.40
            else:
                prob_pago = 0.30
        else:
            if mes <= 6:
                prob_pago = 0.85
            elif mes <= 9:
                prob_pago = 0.70
            else:
                prob_pago = 0.60
        
        if random.random() < prob_pago:
            estado = 'PAGADO'
            dia_pago = random.randint(1, 28)
            fecha_pago = datetime(anio, mes, dia_pago)
            monto_pagado = monto_mensual
            metodo = random.choice(['EFECTIVO', 'TRANSFERENCIA', 'TARJETA'])
        elif random.random() < 0.3:
            estado = 'PARCIAL'
            dia_pago = random.randint(1, 28)
            fecha_pago = datetime(anio, mes, dia_pago)
            monto_pagado = round(monto_mensual * random.uniform(0.3, 0.7), 2)
            metodo = random.choice(['EFECTIVO', 'TRANSFERENCIA'])
        else:
            estado = 'PENDIENTE'
            fecha_pago = None
            monto_pagado = 0
            metodo = None
        
        bulk_pagos.append((
            matricula_id, 'MENSUALIDAD', mes, monto_mensual, monto_pagado,
            fecha_vencimiento, fecha_pago, estado, metodo
        ))
        total_pagos += 1
        
        if len(bulk_pagos) >= 10000:
            cursor.executemany("""
                INSERT INTO pagos (matricula_id, concepto, mes_correspondiente, 
                                 monto_total, monto_pagado, fecha_vencimiento, 
                                 fecha_pago, estado, metodo_pago) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, bulk_pagos)
            conn.commit()
            bulk_pagos = []

if bulk_pagos:
    cursor.executemany("""
        INSERT INTO pagos (matricula_id, concepto, mes_correspondiente, 
                         monto_total, monto_pagado, fecha_vencimiento, 
                         fecha_pago, estado, metodo_pago) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, bulk_pagos)
    conn.commit()

print(f"  Total pagos generados: {total_pagos}")

# ==================================================
# 12. GENERACIÓN DE FICHAS MÉDICAS (CORREGIDO)
# ==================================================

print("-> Generando fichas médicas...")

tipos_sangre = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
alergias_comunes = ['Ninguna', 'Polvo', 'Penicilina', 'Nueces', 'Lactosa', 'Gluten', 'Polen']
condiciones_cronicas = ['Ninguna', 'Asma', 'Diabetes', 'Hipertensión', 'Epilepsia', 'Alergias respiratorias']

bulk_fichas = []
estudiantes_procesados = set()  # Para evitar duplicados

for estudiante in all_estudiantes:
    estudiante_id = estudiante['estudiante_id']
    
    # Saltar si ya se procesó este estudiante
    if estudiante_id in estudiantes_procesados:
        continue
    
    estudiantes_procesados.add(estudiante_id)
    
    apellidos = estudiante.get('apellidos', 'Desconocido')
    
    contacto_nombre = f"Apoderado de {apellidos.split()[0] if apellidos else 'Desconocido'}"
    contacto_telefono = generar_celular_peruano()
    
    num_alergias = random.randint(0, 2)
    alergias_seleccionadas = random.sample(alergias_comunes, min(num_alergias + 1, len(alergias_comunes)))
    alergias = ', '.join([a for a in alergias_seleccionadas if a != 'Ninguna']) or 'Ninguna'
    
    condiciones = random.choice(condiciones_cronicas)
    
    bulk_fichas.append((
        estudiante_id,
        random.choice(tipos_sangre),
        alergias,
        condiciones,
        contacto_nombre,
        contacto_telefono
    ))

# Insertar en lotes para evitar problemas de memoria
batch_size = 1000
for i in range(0, len(bulk_fichas), batch_size):
    batch = bulk_fichas[i:i+batch_size]
    cursor.executemany("""
        INSERT INTO fichas_medicas (estudiante_id, tipo_sangre, alergias, 
                                  condiciones_cronicas, contacto_emergencia_nombre, 
                                  contacto_emergencia_telefono) 
        VALUES (%s, %s, %s, %s, %s, %s)
    """, batch)
    conn.commit()

print(f"  Total fichas médicas generadas: {len(bulk_fichas)}")

# ==================================================
# 13. GENERACIÓN DE ATENCIONES DE ENFERMERÍA (CORREGIDO)
# ==================================================

print("-> Generando atenciones de enfermería...")

sintomas_comunes = [
    'Dolor de cabeza', 'Malestar estomacal', 'Fiebre', 'Dolor de garganta',
    'Tos', 'Congestión nasal', 'Dolores musculares', 'Mareos',
    'Náuseas', 'Vómitos', 'Diarrea', 'Alergia', 'Lesión leve'
]

tratamientos = [
    'Administración de paracetamol', 'Reposo en camilla', 'Aplicación de hielo',
    'Lavado de herida', 'Administración de antihistamínico', 'Toma de temperatura',
    'Hidratación', 'Aplicación de crema', 'Vendaje', 'Observación'
]

bulk_atenciones = []
total_atenciones = 0

# Obtener lista única de estudiantes
estudiantes_unicos = []
estudiantes_ids_vistos = set()
for e in all_estudiantes:
    if e['estudiante_id'] not in estudiantes_ids_vistos:
        estudiantes_ids_vistos.add(e['estudiante_id'])
        estudiantes_unicos.append(e)

estudiantes_con_atenciones = random.sample(estudiantes_unicos, int(len(estudiantes_unicos) * 0.25))

for estudiante in estudiantes_con_atenciones:
    estudiante_id = estudiante['estudiante_id']
    anio = estudiante['anio']
    
    num_atenciones = random.randint(1, 3)
    
    for _ in range(num_atenciones):
        sintoma = random.choice(sintomas_comunes)
        tratamiento = random.choice(tratamientos)
        deriva = random.choice([0, 0, 0, 1])
        
        mes = random.randint(3, 11)
        dia = random.randint(1, 28)
        hora = random.randint(8, 15)
        minuto = random.randint(0, 59)
        
        fecha_hora = datetime(anio, mes, dia, hora, minuto)
        
        bulk_atenciones.append((estudiante_id, fecha_hora, sintoma, tratamiento, deriva))
        total_atenciones += 1
        
        if len(bulk_atenciones) >= 1000:
            cursor.executemany("""
                INSERT INTO atenciones_enfermeria (estudiante_id, fecha_hora, 
                                                  sintomas, tratamiento_aplicado, 
                                                  deriva_hospital) 
                VALUES (%s, %s, %s, %s, %s)
            """, bulk_atenciones)
            conn.commit()
            bulk_atenciones = []

if bulk_atenciones:
    cursor.executemany("""
        INSERT INTO atenciones_enfermeria (estudiante_id, fecha_hora, 
                                          sintomas, tratamiento_aplicado, 
                                          deriva_hospital) 
        VALUES (%s, %s, %s, %s, %s)
    """, bulk_atenciones)
    conn.commit()

print(f"  Total atenciones de enfermería generadas: {total_atenciones}")

# ==================================================
# 14. GENERACIÓN DE REPORTES DISCIPLINARIOS
# ==================================================

print("-> Generando reportes disciplinarios...")

reportes_disciplinarios = [
    ('LEVE', 'Llamado de atención por comportamiento inapropiado en clase'),
    ('LEVE', 'Uso incorrecto del uniforme escolar'),
    ('LEVE', 'Llegar tarde repetidamente a clases'),
    ('LEVE', 'No entregar tareas a tiempo'),
    ('MODERADA', 'Uso de celular en clase sin autorización'),
    ('MODERADA', 'Falta de respeto hacia compañeros'),
    ('MODERADA', 'Interrupción constante de clases'),
    ('MODERADA', 'Copiar en evaluaciones'),
    ('GRAVE', 'Falta de respeto grave hacia un docente'),
    ('GRAVE', 'Acoso escolar (bullying)'),
    ('GRAVE', 'Daño a propiedad del colegio'),
    ('MUY GRAVE', 'Agresión física a compañero'),
    ('MUY GRAVE', 'Porte de objetos peligrosos'),
    ('MUY GRAVE', 'Consumo de sustancias prohibidas en el colegio')
]

sanciones = {
    'LEVE': ['Llamado de atención verbal', 'Amonestación escrita', 'Tarea extra'],
    'MODERADA': ['Citación a padres', 'Suspensión de recreo', 'Trabajo comunitario'],
    'GRAVE': ['Suspensión de 1 día', 'Citación a directiva', 'Plan de mejora conductual'],
    'MUY GRAVE': ['Suspensión de 3 días', 'Matrícula condicional', 'Traslado de sección']
}

bulk_reportes = []
total_reportes = 0

# Incluir más repitentes en reportes (selección con peso)
estudiantes_con_peso = []
for e in all_estudiantes:
    peso = 1
    if es_repitente_map.get(e['estudiante_id'], False):
        peso = 4
    estudiantes_con_peso.extend([e] * peso)

estudiantes_con_reportes = random.sample(
    estudiantes_con_peso, 
    min(int(len(all_estudiantes) * 0.12), len(estudiantes_con_peso))
)

for estudiante in estudiantes_con_reportes:
    estudiante_id = estudiante['estudiante_id']
    seccion_id = estudiante['seccion_id']
    periodo_id = estudiante['periodo_id']
    anio = estudiante['anio']
    
    num_reportes = random.randint(1, 2)
    
    for _ in range(num_reportes):
        gravedad, descripcion = random.choice(reportes_disciplinarios)
        sancion = random.choice(sanciones[gravedad])
        
        mes = random.randint(3, 11)
        dia = random.randint(1, 28)
        fecha = datetime(anio, mes, dia)
        
        cursor.execute("""
            SELECT profesor_id FROM asignaciones_profesor 
            WHERE seccion_id = %s AND periodo_id = %s 
            LIMIT 1
        """, (seccion_id, periodo_id))
        profesor_reporta = cursor.fetchone()
        
        if profesor_reporta:
            profesor_id = profesor_reporta[0]
            bulk_reportes.append((estudiante_id, profesor_id, fecha, gravedad, descripcion, sancion))
            total_reportes += 1
            
            if len(bulk_reportes) >= 1000:
                cursor.executemany("""
                    INSERT INTO reportes_disciplinarios (estudiante_id, profesor_reporta_id, 
                                                        fecha_incidente, gravedad, 
                                                        descripcion, sancion_aplicada) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, bulk_reportes)
                conn.commit()
                bulk_reportes = []

if bulk_reportes:
    cursor.executemany("""
        INSERT INTO reportes_disciplinarios (estudiante_id, profesor_reporta_id, 
                                            fecha_incidente, gravedad, 
                                            descripcion, sancion_aplicada) 
        VALUES (%s, %s, %s, %s, %s, %s)
    """, bulk_reportes)
    conn.commit()

print(f"  Total reportes disciplinarios generados: {total_reportes}")

# ==================================================
# 15. GENERACIÓN DE PRÉSTAMOS DE BIBLIOTECA
# ==================================================

print("-> Generando préstamos de biblioteca...")

cursor.execute("SELECT id FROM libros")
libros_ids = [row[0] for row in cursor.fetchall()]

bulk_prestamos = []
total_prestamos = 0

estudiantes_con_prestamos = random.sample(all_estudiantes, int(len(all_estudiantes) * 0.35))

for estudiante in estudiantes_con_prestamos:
    persona_id = estudiante['persona_id']
    anio = estudiante['anio']
    
    num_prestamos = random.randint(1, 3)
    
    for _ in range(num_prestamos):
        libro_id = random.choice(libros_ids)
        
        mes_prestamo = random.randint(3, 11)
        dia_prestamo = random.randint(1, 28)
        fecha_prestamo = datetime(anio, mes_prestamo, dia_prestamo)
        
        fecha_devolucion_esperada = fecha_prestamo + timedelta(days=14)
        
        estado_prob = random.random()
        if estado_prob < 0.7:
            estado = 'DEVUELTO'
            dias_dev = random.randint(10, 16)
            fecha_devolucion_real = fecha_prestamo + timedelta(days=dias_dev)
        elif estado_prob < 0.85:
            estado = 'PRESTADO'
            fecha_devolucion_real = None
        elif estado_prob < 0.95:
            estado = 'ATRASADO'
            fecha_devolucion_real = None
        else:
            estado = 'PERDIDO'
            fecha_devolucion_real = None
        
        bulk_prestamos.append((libro_id, persona_id, fecha_prestamo, 
                             fecha_devolucion_esperada, fecha_devolucion_real, estado))
        total_prestamos += 1
        
        if len(bulk_prestamos) >= 5000:
            cursor.executemany("""
                INSERT INTO prestamos_biblioteca (libro_id, persona_id, fecha_prestamo, 
                                                fecha_devolucion_esperada, fecha_devolucion_real, estado) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, bulk_prestamos)
            conn.commit()
            bulk_prestamos = []

if bulk_prestamos:
    cursor.executemany("""
        INSERT INTO prestamos_biblioteca (libro_id, persona_id, fecha_prestamo, 
                                        fecha_devolucion_esperada, fecha_devolucion_real, estado) 
        VALUES (%s, %s, %s, %s, %s, %s)
    """, bulk_prestamos)
    conn.commit()

print(f"  Total préstamos de biblioteca generados: {total_prestamos}")

# ==================================================
# 16. ESTADÍSTICAS FINALES
# ==================================================

print("==================================================")
print("¡PROCESO COMPLETADO EXITOSAMENTE!")

cursor.execute("SELECT COUNT(*) FROM estudiantes")
total_estudiantes = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM profesores")
total_profesores = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM notas")
total_notas = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM asistencias_estudiantes")
total_asistencias = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM pagos")
total_pagos = cursor.fetchone()[0]

# Contar estudiantes repitentes (los que tienen más de una matrícula)
cursor.execute("""
    SELECT COUNT(DISTINCT estudiante_id) 
    FROM matriculas 
    GROUP BY estudiante_id 
    HAVING COUNT(*) > 1
""")
repitentes = cursor.fetchall()
total_repitentes = len(repitentes)

print("\nEstadísticas generadas:")
print(f"  - Estudiantes: {total_estudiantes}")
print(f"  - Estudiantes Repitentes: {total_repitentes}")
print(f"  - Profesores: {total_profesores}")
print(f"  - Notas: {total_notas}")
print(f"  - Asistencias: {total_asistencias}")
print(f"  - Pagos: {total_pagos}")
print("==================================================")

cursor.close()
conn.close()