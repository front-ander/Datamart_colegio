
-- DATA MART COLEGIO - MODELO ESTRELLA
-- Base de datos: datamart_colegio

USE master;
GO

-- Eliminar base de datos si existe (para empezar limpio)
IF EXISTS (SELECT name FROM sys.databases WHERE name = 'datamart_colegio')
BEGIN
    ALTER DATABASE datamart_colegio SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE datamart_colegio;
END
GO

-- Crear base de datos
CREATE DATABASE datamart_colegio;
GO

USE datamart_colegio;
GO

-- 1. TABLAS DIMENSIÓN

CREATE TABLE DimTiempo (
    id_tiempo INT PRIMARY KEY,
    fecha DATE NOT NULL,
    anio INT NOT NULL,
    mes INT NOT NULL,
    nombre_mes VARCHAR(20) NOT NULL,
    bimestre INT NOT NULL
);
GO

CREATE TABLE DimEstudiante (
    id_estudiante_sk INT IDENTITY(1,1) PRIMARY KEY,
    id_estudiante_oltp BIGINT,
    codigo_estudiante VARCHAR(50),
    nombre_completo VARCHAR(200),
    grado_academico VARCHAR(50)
);
GO

CREATE TABLE DimCurso (
    id_curso_sk INT IDENTITY(1,1) PRIMARY KEY,
    id_curso_oltp INT,
    nombre_curso VARCHAR(100),
    area_conocimiento VARCHAR(100)
);
GO

CREATE TABLE DimProfesor (
    id_profesor_sk INT IDENTITY(1,1) PRIMARY KEY,
    id_profesor_oltp BIGINT,
    nombre_completo VARCHAR(200),
    especialidad VARCHAR(100)
);
GO

CREATE TABLE DimGradoSeccion (
    id_grado_seccion_sk INT IDENTITY(1,1) PRIMARY KEY,
    grado VARCHAR(50) NOT NULL,
    seccion VARCHAR(10) NOT NULL,
    turno VARCHAR(20),
    nivel VARCHAR(50)
);
GO

-- 2. TABLA DE HECHOS

CREATE TABLE HechoRendimientoAcademico (
    id_hecho BIGINT IDENTITY(1,1) PRIMARY KEY,
    id_tiempo INT NOT NULL,
    id_estudiante_sk INT NOT NULL,
    id_curso_sk INT NOT NULL,
    id_profesor_sk INT NOT NULL,
    id_grado_seccion_sk INT NOT NULL,
    bimestre INT NOT NULL,
    nota_obtenida DECIMAL(5,2),
    cantidad_asistencias INT DEFAULT 0,
    cantidad_tardanzas INT DEFAULT 0,
    cantidad_ausencias INT DEFAULT 0
);
GO

-- 3. FOREIGN KEYS

ALTER TABLE HechoRendimientoAcademico 
ADD CONSTRAINT FK_Hecho_DimTiempo 
FOREIGN KEY (id_tiempo) REFERENCES DimTiempo(id_tiempo);
GO

ALTER TABLE HechoRendimientoAcademico 
ADD CONSTRAINT FK_Hecho_DimEstudiante 
FOREIGN KEY (id_estudiante_sk) REFERENCES DimEstudiante(id_estudiante_sk);
GO

ALTER TABLE HechoRendimientoAcademico 
ADD CONSTRAINT FK_Hecho_DimCurso 
FOREIGN KEY (id_curso_sk) REFERENCES DimCurso(id_curso_sk);
GO

ALTER TABLE HechoRendimientoAcademico 
ADD CONSTRAINT FK_Hecho_DimProfesor 
FOREIGN KEY (id_profesor_sk) REFERENCES DimProfesor(id_profesor_sk);
GO

ALTER TABLE HechoRendimientoAcademico 
ADD CONSTRAINT FK_Hecho_DimGradoSeccion 
FOREIGN KEY (id_grado_seccion_sk) REFERENCES DimGradoSeccion(id_grado_seccion_sk);
GO

-- 4. ÍNDICES

-- Índices para claves foráneas
CREATE INDEX IX_Hecho_Tiempo ON HechoRendimientoAcademico(id_tiempo);
CREATE INDEX IX_Hecho_Estudiante ON HechoRendimientoAcademico(id_estudiante_sk);
CREATE INDEX IX_Hecho_Curso ON HechoRendimientoAcademico(id_curso_sk);
CREATE INDEX IX_Hecho_Profesor ON HechoRendimientoAcademico(id_profesor_sk);
CREATE INDEX IX_Hecho_GradoSeccion ON HechoRendimientoAcademico(id_grado_seccion_sk);

-- Índices para KPIs
CREATE INDEX IX_Hecho_NotaEstudiante ON HechoRendimientoAcademico(nota_obtenida, id_estudiante_sk);
CREATE INDEX IX_Hecho_NotaDesc ON HechoRendimientoAcademico(nota_obtenida DESC);
CREATE INDEX IX_Hecho_Ausencias ON HechoRendimientoAcademico(cantidad_ausencias, id_estudiante_sk);
CREATE INDEX IX_Hecho_CursoProfesor ON HechoRendimientoAcademico(id_curso_sk, id_profesor_sk);
CREATE INDEX IX_Hecho_TiempoBimestre ON HechoRendimientoAcademico(id_tiempo, bimestre);
GO

-- 5. VISTA DE CONSULTA EJEMPLO

CREATE OR ALTER VIEW vw_RendimientoAcademico AS
SELECT 
    e.nombre_completo AS Estudiante,
    e.codigo_estudiante AS Codigo,
    e.grado_academico AS Grado,
    c.nombre_curso AS Curso,
    c.area_conocimiento AS Area,
    p.nombre_completo AS Profesor,
    p.especialidad AS EspecialidadProfesor,
    g.seccion AS Seccion,
    g.turno AS Turno,
    t.anio AS Anio,
    t.bimestre AS Bimestre,
    h.nota_obtenida AS Nota,
    h.cantidad_asistencias AS Asistencias,
    h.cantidad_tardanzas AS Tardanzas,
    h.cantidad_ausencias AS Ausencias,
    CASE 
        WHEN h.nota_obtenida >= 11 THEN 'APROBADO'
        ELSE 'DESAPROBADO'
    END AS Estado
FROM HechoRendimientoAcademico h
INNER JOIN DimEstudiante e ON h.id_estudiante_sk = e.id_estudiante_sk
INNER JOIN DimCurso c ON h.id_curso_sk = c.id_curso_sk
INNER JOIN DimProfesor p ON h.id_profesor_sk = p.id_profesor_sk
INNER JOIN DimTiempo t ON h.id_tiempo = t.id_tiempo
INNER JOIN DimGradoSeccion g ON h.id_grado_seccion_sk = g.id_grado_seccion_sk;
GO

-- =============================================
-- 6. VERIFICACIÓN FINAL
-- =============================================

-- Mostrar todas las tablas
PRINT '==========================================';
PRINT 'TABLAS CREADAS:';
PRINT '==========================================';
SELECT 
    name AS Tabla,
    CASE 
        WHEN name = 'HechoRendimientoAcademico' THEN 'HECHO'
        ELSE 'DIMENSIÓN'
    END AS Tipo
FROM sys.tables 
WHERE type = 'U'
ORDER BY CASE WHEN name = 'HechoRendimientoAcademico' THEN 1 ELSE 0 END, name;
GO

-- Mostrar todas las FOREIGN KEY
PRINT '';
PRINT '==========================================';
PRINT 'FOREIGN KEYS CREADAS:';
PRINT '==========================================';
SELECT 
    fk.name AS Nombre_FK,
    OBJECT_NAME(fk.parent_object_id) AS Tabla_Hija,
    OBJECT_NAME(fk.referenced_object_id) AS Tabla_Padre
FROM sys.foreign_keys fk
ORDER BY fk.name;
GO

-- Mostrar cantidad de índices
PRINT '';
PRINT '==========================================';
PRINT 'ÍNDICES CREADOS:';
PRINT '==========================================';
SELECT 
    t.name AS Tabla,
    COUNT(i.index_id) AS CantidadIndices
FROM sys.tables t
LEFT JOIN sys.indexes i ON t.object_id = i.object_id AND i.index_id > 0
WHERE t.type = 'U'
GROUP BY t.name
ORDER BY t.name;
GO