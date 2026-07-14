USE datamart_colegio;
GO

-- =================================================================================
-- KPI 1: Tasa de Desaprobación General (Por Promedio del Alumno)
-- =================================================================================
WITH PromediosEstudiante AS (
    SELECT 
        e.id_estudiante_sk,
        e.nombre_completo,
        e.grado_academico,
        t.anio,
        AVG(h.nota_obtenida) AS promedio_final
    FROM HechoRendimientoAcademico h
    INNER JOIN DimEstudiante e ON h.id_estudiante_sk = e.id_estudiante_sk
    INNER JOIN DimTiempo t ON h.id_tiempo = t.id_tiempo
    GROUP BY e.id_estudiante_sk, e.nombre_completo, e.grado_academico, t.anio
)
SELECT 
    anio AS Año,
    COUNT(*) AS Total_Estudiantes,
    SUM(CASE WHEN promedio_final < 11 THEN 1 ELSE 0 END) AS Desaprobados,
    CONCAT(
        ROUND(
            CAST(SUM(CASE WHEN promedio_final < 11 THEN 1 ELSE 0 END) AS FLOAT) 
            / COUNT(*) * 100, 2
        ), ' %'
    ) AS Tasa_Desaprobacion
FROM PromediosEstudiante
GROUP BY anio
ORDER BY anio DESC;
GO

-- =================================================================================
-- KPI 2: Tasa de Aprobación General (Por Promedio del Alumno)
-- =================================================================================
WITH PromediosEstudiante AS (
    SELECT 
        e.id_estudiante_sk,
        e.nombre_completo,
        e.grado_academico,
        t.anio,
        AVG(h.nota_obtenida) AS promedio_final
    FROM HechoRendimientoAcademico h
    INNER JOIN DimEstudiante e ON h.id_estudiante_sk = e.id_estudiante_sk
    INNER JOIN DimTiempo t ON h.id_tiempo = t.id_tiempo
    GROUP BY e.id_estudiante_sk, e.nombre_completo, e.grado_academico, t.anio
)
SELECT 
    anio AS Año,
    COUNT(*) AS Total_Estudiantes,
    SUM(CASE WHEN promedio_final >= 11 THEN 1 ELSE 0 END) AS Aprobados,
    CONCAT(
        ROUND(
            CAST(SUM(CASE WHEN promedio_final >= 11 THEN 1 ELSE 0 END) AS FLOAT) 
            / COUNT(*) * 100, 2
        ), ' %'
    ) AS Tasa_Aprobacion
FROM PromediosEstudiante
GROUP BY anio
ORDER BY anio DESC;
GO

-- =================================================================================
-- KPI 3: Promedio General (CORREGIDO - Nota_Minima era SUM, debe ser MIN)
-- =================================================================================
SELECT 
    t.anio AS Año,
    t.bimestre AS Bimestre,
    COUNT(*) AS Total_Notas,
    ROUND(AVG(h.nota_obtenida), 2) AS Promedio_General,
    ROUND(MIN(h.nota_obtenida), 2) AS Nota_Minima,
    ROUND(MAX(h.nota_obtenida), 2) AS Nota_Maxima,
    ROUND(STDEV(h.nota_obtenida), 2) AS Desviacion_Estandar
FROM HechoRendimientoAcademico h
INNER JOIN DimTiempo t ON h.id_tiempo = t.id_tiempo
GROUP BY t.anio, t.bimestre
ORDER BY t.anio DESC, t.bimestre;
GO

-- =================================================================================
-- KPI 4: Tasa de Retención (CORREGIDO - estaba mal la fórmula)
-- =================================================================================
WITH EstudiantesPorAnio AS (
    SELECT DISTINCT
        e.id_estudiante_sk,
        t.anio
    FROM HechoRendimientoAcademico h
    INNER JOIN DimEstudiante e ON h.id_estudiante_sk = e.id_estudiante_sk
    INNER JOIN DimTiempo t ON h.id_tiempo = t.id_tiempo
)
SELECT 
    a1.anio AS Año_Actual,
    COUNT(DISTINCT a1.id_estudiante_sk) AS Estudiantes_Actual,
    COUNT(DISTINCT a2.id_estudiante_sk) AS Estudiantes_Anterior,
    CONCAT(
        ROUND(
            CAST(COUNT(DISTINCT a2.id_estudiante_sk) AS FLOAT) 
            / NULLIF(COUNT(DISTINCT a1.id_estudiante_sk), 0) * 100, 2
        ), ' %'
    ) AS Tasa_Retencion
FROM EstudiantesPorAnio a1
LEFT JOIN EstudiantesPorAnio a2 
    ON a1.id_estudiante_sk = a2.id_estudiante_sk 
    AND a2.anio = a1.anio - 1
GROUP BY a1.anio
HAVING a1.anio > (SELECT MIN(anio) FROM EstudiantesPorAnio)
ORDER BY a1.anio DESC;
GO

-- =================================================================================
-- KPI 5: Índice de Riesgo por Ausentismo
-- =================================================================================
SELECT TOP 20
    e.nombre_completo AS Estudiante,
    e.grado_academico AS Grado,
    t.anio AS Año,
    SUM(h.cantidad_ausencias) AS Total_Ausencias,
    SUM(h.cantidad_tardanzas) AS Total_Tardanzas,
    SUM(h.cantidad_asistencias) AS Total_Asistencias,
    CONCAT(
        ROUND(
            CASE 
                WHEN (SUM(h.cantidad_asistencias) + SUM(h.cantidad_ausencias) + SUM(h.cantidad_tardanzas)) > 0
                THEN SUM(h.cantidad_asistencias) * 100.0 / 
                    (SUM(h.cantidad_asistencias) + SUM(h.cantidad_ausencias) + SUM(h.cantidad_tardanzas))
                ELSE 0
            END, 2
        ), ' %'
    ) AS Asistencia_Promedio,
    CASE 
        WHEN SUM(h.cantidad_ausencias) >= 15 THEN 'CRÍTICO'
        WHEN SUM(h.cantidad_ausencias) >= 10 THEN 'ALTO'
        WHEN SUM(h.cantidad_ausencias) >= 5 THEN 'MODERADO'
        ELSE 'BAJO'
    END AS Nivel_Riesgo
FROM HechoRendimientoAcademico h
INNER JOIN DimEstudiante e ON h.id_estudiante_sk = e.id_estudiante_sk
INNER JOIN DimTiempo t ON h.id_tiempo = t.id_tiempo
GROUP BY e.id_estudiante_sk, e.nombre_completo, e.grado_academico, t.anio
HAVING SUM(h.cantidad_ausencias) > 0
ORDER BY SUM(h.cantidad_ausencias) DESC;
GO

-- =================================================================================
-- KPI 6: Desempeño por Curso
-- =================================================================================
SELECT 
    c.nombre_curso AS Curso,
    c.area_conocimiento AS Area,
    t.anio AS Año,
    COUNT(*) AS Total_Notas,
    ROUND(AVG(h.nota_obtenida), 2) AS Promedio,
    ROUND(MIN(h.nota_obtenida), 2) AS Minimo,
    ROUND(MAX(h.nota_obtenida), 2) AS Maximo,
    CONCAT(
        ROUND(
            SUM(CASE WHEN h.nota_obtenida >= 11 THEN 1 ELSE 0 END) 
            / CAST(COUNT(*) AS FLOAT) * 100, 2
        ), ' %'
    ) AS Tasa_Aprobacion
FROM HechoRendimientoAcademico h
INNER JOIN DimCurso c ON h.id_curso_sk = c.id_curso_sk
INNER JOIN DimTiempo t ON h.id_tiempo = t.id_tiempo
GROUP BY c.nombre_curso, c.area_conocimiento, t.anio
ORDER BY t.anio DESC, Promedio DESC;
GO

-- =================================================================================
-- KPI 7: Promedio por Grado
-- =================================================================================
SELECT 
    g.grado AS Grado,
    g.seccion AS Seccion,
    g.nivel AS Nivel,
    t.anio AS Año,
    COUNT(DISTINCT h.id_estudiante_sk) AS Total_Estudiantes,
    COUNT(*) AS Total_Notas,
    ROUND(AVG(h.nota_obtenida), 2) AS Promedio_General,
    CONCAT(
        ROUND(
            SUM(CASE WHEN h.nota_obtenida >= 11 THEN 1 ELSE 0 END) 
            / CAST(COUNT(*) AS FLOAT) * 100, 2
        ), ' %'
    ) AS Tasa_Aprobacion
FROM HechoRendimientoAcademico h
INNER JOIN DimGradoSeccion g ON h.id_grado_seccion_sk = g.id_grado_seccion_sk
INNER JOIN DimTiempo t ON h.id_tiempo = t.id_tiempo
GROUP BY g.grado, g.seccion, g.nivel, t.anio
ORDER BY t.anio DESC, g.nivel, g.grado;
GO

-- =================================================================================
-- KPI 8: Tasa de Ausentismo
-- =================================================================================
SELECT 
    t.anio AS Año,
    SUM(h.cantidad_ausencias) AS Total_Ausencias,
    SUM(h.cantidad_asistencias) AS Total_Asistencias,
    SUM(h.cantidad_tardanzas) AS Total_Tardanzas,
    CONCAT(
        ROUND(
            SUM(h.cantidad_ausencias) 
            / CAST(NULLIF(SUM(h.cantidad_asistencias + h.cantidad_ausencias + h.cantidad_tardanzas), 0) AS FLOAT) 
            * 100, 2
        ), ' %'
    ) AS Tasa_Ausentismo
FROM HechoRendimientoAcademico h
INNER JOIN DimTiempo t ON h.id_tiempo = t.id_tiempo
GROUP BY t.anio
ORDER BY t.anio DESC;
GO

-- =================================================================================
-- KPI 9: Tasa de Tardanzas
-- =================================================================================
SELECT 
    t.anio AS Año,
    g.grado AS Grado,
    g.seccion AS Seccion,
    SUM(h.cantidad_tardanzas) AS Total_Tardanzas,
    CONCAT(
        ROUND(
            SUM(h.cantidad_tardanzas) 
            / CAST(NULLIF(SUM(h.cantidad_asistencias + h.cantidad_ausencias + h.cantidad_tardanzas), 0) AS FLOAT) 
            * 100, 2
        ), ' %'
    ) AS Tasa_Tardanzas
FROM HechoRendimientoAcademico h
INNER JOIN DimTiempo t ON h.id_tiempo = t.id_tiempo
INNER JOIN DimGradoSeccion g ON h.id_grado_seccion_sk = g.id_grado_seccion_sk
GROUP BY t.anio, g.grado, g.seccion
HAVING SUM(h.cantidad_tardanzas) > 0
ORDER BY t.anio DESC, Tasa_Tardanzas DESC;
GO

-- =================================================================================
-- KPI 10: Top 10 Estudiantes en Riesgo
-- =================================================================================
SELECT TOP 10
    e.nombre_completo AS Estudiante,
    e.grado_academico AS Grado,
    t.anio AS Año,
    ROUND(AVG(h.nota_obtenida), 2) AS Promedio_Notas,
    SUM(h.cantidad_ausencias) AS Total_Ausencias,
    COUNT(CASE WHEN h.nota_obtenida < 11 THEN 1 END) AS Notas_Desaprobadas,
    ROUND(
        (1 - AVG(h.nota_obtenida) / 20) * 40 + 
        (SUM(h.cantidad_ausencias) / 20) * 30 +
        (COUNT(CASE WHEN h.nota_obtenida < 11 THEN 1 END) / 50) * 30, 
        2
    ) AS Indice_Riesgo_Global
FROM HechoRendimientoAcademico h
INNER JOIN DimEstudiante e ON h.id_estudiante_sk = e.id_estudiante_sk
INNER JOIN DimTiempo t ON h.id_tiempo = t.id_tiempo
GROUP BY e.id_estudiante_sk, e.nombre_completo, e.grado_academico, t.anio
ORDER BY Indice_Riesgo_Global DESC;
GO

-- =================================================================================
-- KPI 11: Promedio por Docente
-- =================================================================================
SELECT 
    p.nombre_completo AS Profesor,
    p.especialidad AS Especialidad,
    t.anio AS Año,
    COUNT(DISTINCT h.id_curso_sk) AS Cursos_Asignados,
    COUNT(DISTINCT h.id_estudiante_sk) AS Total_Estudiantes,
    COUNT(*) AS Total_Notas,
    ROUND(AVG(h.nota_obtenida), 2) AS Promedio_Notas,
    CONCAT(
        ROUND(
            SUM(CASE WHEN h.nota_obtenida >= 11 THEN 1 ELSE 0 END) 
            / CAST(COUNT(*) AS FLOAT) * 100, 2
        ), ' %'
    ) AS Tasa_Aprobacion
FROM HechoRendimientoAcademico h
INNER JOIN DimProfesor p ON h.id_profesor_sk = p.id_profesor_sk
INNER JOIN DimTiempo t ON h.id_tiempo = t.id_tiempo
GROUP BY p.nombre_completo, p.especialidad, t.anio
HAVING COUNT(*) > 0
ORDER BY t.anio DESC, Promedio_Notas DESC;
GO

-- =================================================================================
-- KPI 12: Variabilidad por Docente
-- =================================================================================
SELECT 
    p.nombre_completo AS Profesor,
    p.especialidad AS Especialidad,
    t.anio AS Año,
    COUNT(*) AS Total_Notas,
    ROUND(AVG(h.nota_obtenida), 2) AS Promedio,
    ROUND(STDEV(h.nota_obtenida), 2) AS Desviacion_Estandar,
    ROUND(MIN(h.nota_obtenida), 2) AS Nota_Minima,
    ROUND(MAX(h.nota_obtenida), 2) AS Nota_Maxima,
    CASE 
        WHEN STDEV(h.nota_obtenida) > 5 THEN 'ALTA VARIABILIDAD'
        WHEN STDEV(h.nota_obtenida) > 3 THEN 'VARIABILIDAD MODERADA'
        ELSE 'BAJA VARIABILIDAD'
    END AS Nivel_Variabilidad
FROM HechoRendimientoAcademico h
INNER JOIN DimProfesor p ON h.id_profesor_sk = p.id_profesor_sk
INNER JOIN DimTiempo t ON h.id_tiempo = t.id_tiempo
GROUP BY p.nombre_completo, p.especialidad, t.anio
HAVING COUNT(*) >= 10
ORDER BY t.anio DESC, Desviacion_Estandar DESC;
GO