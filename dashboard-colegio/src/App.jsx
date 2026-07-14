import React, { useState } from 'react';
import FilterPanel from './components/FilterPanel';
import VistaResumenKpis from './components/VistaResumenKpis';
import VistaEvolucionAprobacion from './components/VistaEvolucionAprobacion';
import VistaRendimientoDocente from './components/VistaRendimientoDocente';
import VistaRiesgoCritico from './components/VistaRiesgoCritico';
import VistaRendimientoAnual from './components/VistaRendimientoAnual';
import VistaAsistencia from './components/VistaAsistencia';
import VistaCursos from './components/VistaCursos';
import VistaDesaprobados from './components/VistaDesaprobados';
import VistaGradosAcademicos from './components/VistaGradosAcademicos';
import EtlMonitor from './components/EtlMonitor';

function App() {
  const [activeTab, setActiveTab] = useState('v-resumen');
  const [filters, setFilters] = useState({ anio: '', grado: '' });

  const navItems = [
    { id: 'v-resumen', icon: 'fa-solid fa-chart-pie', label: 'Visión General de KPIs' },
    { id: 'v-evolucion', icon: 'fa-solid fa-chart-line', label: 'Evolución de Aprobación' },
    { id: 'v-rendimiento', icon: 'fa-solid fa-table', label: 'Detalle de Rendimiento' },
    { id: 'v-riesgo', icon: 'fa-solid fa-triangle-exclamation', label: 'Riesgo Crítico y Faltas' },
    { id: 'v-asistencia', icon: 'fa-solid fa-calendar-check', label: 'Tendencias de Asistencia' },
    { id: 'v-docentes', icon: 'fa-solid fa-chalkboard-user', label: 'Rendimiento por Docente' },
    { id: 'v-cursos', icon: 'fa-solid fa-book-open', label: 'Distribución de Cursos' },
    { id: 'v-desaprobados', icon: 'fa-solid fa-user-xmark', label: 'Análisis de Desaprobados' },
    { id: 'v-grados', icon: 'fa-solid fa-graduation-cap', label: 'Desempeño por Grado' },
    { id: 'v-etl', icon: 'fa-solid fa-database', label: 'Monitor de Pipeline ETL' }
  ];

  const renderContent = () => {
    switch(activeTab) {
      case 'v-resumen': return <VistaResumenKpis filters={filters} />;
      case 'v-evolucion': return <VistaEvolucionAprobacion filters={filters} />;
      case 'v-rendimiento': return <VistaRendimientoAnual filters={filters} />;
      case 'v-riesgo': return <VistaRiesgoCritico filters={filters} />;
      case 'v-asistencia': return <VistaAsistencia filters={filters} />;
      case 'v-docentes': return <VistaRendimientoDocente filters={filters} />;
      case 'v-cursos': return <VistaCursos filters={filters} />;
      case 'v-desaprobados': return <VistaDesaprobados filters={filters} />;
      case 'v-grados': return <VistaGradosAcademicos filters={filters} />;
      case 'v-etl': return <EtlMonitor />;
      default: return null;
    }
  };

  const currentTabName = navItems.find(n => n.id === activeTab)?.label || '';

  return (
    <div className="app-container">
      <div className="sidebar">
        <div className="sidebar-header">
          <h2>DATAMART COLEGIO</h2>
        </div>
        <div className="sidebar-nav">
          {navItems.map(item => (
            <a 
              key={item.id}
              href="#" 
              className={`nav-item ${activeTab === item.id ? 'active' : ''}`}
              onClick={(e) => { e.preventDefault(); setActiveTab(item.id); }}
            >
              <i className={item.icon}></i>
              {item.label}
            </a>
          ))}
        </div>
      </div>
      
      <div className="main-wrapper">
        <div className="topbar">
          <div className="topbar-title">
            <h1>{currentTabName}</h1>
            <p>Dashboard Operacional — Colegios BI</p>
          </div>
          <FilterPanel filters={filters} setFilters={setFilters} />
        </div>
        <div className="page-content">
          {renderContent()}
        </div>
      </div>
    </div>
  );
}

export default App;
