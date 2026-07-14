import React, { useState, useEffect } from 'react';
import axios from 'axios';

function KpiCards({ filters }) {
  const [kpis, setKpis] = useState({
    total_estudiantes: 0,
    promedio_general: 0,
    total_cursos: 0,
    total_asistencias: 0
  });

  useEffect(() => {
    const params = new URLSearchParams();
    if (filters?.anio) params.append('anio', filters.anio);
    if (filters?.grado) params.append('grado', filters.grado);

    axios.get(`http://127.0.0.1:8000/api/kpis?${params.toString()}`)
      .then(res => setKpis(res.data))
      .catch(err => console.error(err));
  }, [filters]);

  return (
    <div className="kpi-grid">
      <div className="kpi-card contoso-card">
        <div className="kpi-info">
          <p className="kpi-title">Total Estudiantes</p>
          <h3 className="kpi-value">{kpis.total_estudiantes}</h3>
          <p className="kpi-trend success">32.3% vs LY</p>
        </div>
        <div className="kpi-visual">
          <i className="fa-solid fa-users kpi-top-icon"></i>
          <svg className="sparkline" viewBox="0 0 100 30">
             <path d="M0,20 Q25,5 50,20 T100,10" fill="none" stroke="#4facfe" strokeWidth="2" />
          </svg>
        </div>
      </div>
      <div className="kpi-card contoso-card">
        <div className="kpi-info">
          <p className="kpi-title">Promedio General</p>
          <h3 className="kpi-value">{kpis.promedio_general}</h3>
          <p className="kpi-trend success">32.0% vs LY</p>
        </div>
        <div className="kpi-visual">
          <i className="fa-solid fa-star kpi-top-icon"></i>
          <svg className="sparkline" viewBox="0 0 100 30">
             <path d="M0,25 Q25,10 50,15 T100,5" fill="none" stroke="#10b981" strokeWidth="2" />
          </svg>
        </div>
      </div>
      <div className="kpi-card contoso-card">
        <div className="kpi-info">
          <p className="kpi-title">Cursos Activos</p>
          <h3 className="kpi-value">{kpis.total_cursos}</h3>
          <p className="kpi-trend danger">-0.23% vs LY</p>
        </div>
        <div className="kpi-visual">
          <i className="fa-solid fa-book-open kpi-top-icon"></i>
          <svg className="sparkline" viewBox="0 0 100 30">
             <path d="M0,5 Q25,25 50,15 T100,20" fill="none" stroke="#ef4444" strokeWidth="2" />
          </svg>
        </div>
      </div>
      <div className="kpi-card contoso-card">
        <div className="kpi-info">
          <p className="kpi-title">Asistencias Totales</p>
          <h3 className="kpi-value">{kpis.total_asistencias}</h3>
          <p className="kpi-trend success">Achieved: 72.7%</p>
        </div>
        <div className="kpi-visual">
          <i className="fa-solid fa-calendar-check kpi-top-icon"></i>
          <svg className="sparkline" viewBox="0 0 100 30">
             <path d="M0,20 Q25,15 50,25 T100,10" fill="none" stroke="#8b5cf6" strokeWidth="2" />
          </svg>
        </div>
      </div>
    </div>
  );
}
export default KpiCards;
