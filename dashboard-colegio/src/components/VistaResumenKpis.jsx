import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend, AreaChart, Area, XAxis, YAxis, CartesianGrid, BarChart, Bar } from 'recharts';
import KpiCards from './KpiCards';

function VistaResumenKpis({ filters }) {
  const [aprobadosData, setAprobadosData] = useState([]);
  const [asistenciaData, setAsistenciaData] = useState([]);
  const [docentesData, setDocentesData] = useState([]);

  useEffect(() => {
    const params = new URLSearchParams();
    if (filters?.anio) params.append('anio', filters.anio);
    if (filters?.grado) params.append('grado', filters.grado);
    const q = params.toString();

    // Fetch Aprobados vs Desaprobados
    axios.get(`http://127.0.0.1:8000/api/rendimiento?${q}`)
      .then(res => {
        let aprobados = 0;
        let desaprobados = 0;
        res.data.forEach(d => { aprobados += d.aprobados; desaprobados += d.desaprobados; });
        setAprobadosData([
          { name: 'Aprobados', value: aprobados },
          { name: 'Desaprobados', value: desaprobados }
        ]);
      })
      .catch(console.error);

    // Fetch Asistencia (Mocked trend per grade as AreaChart)
    axios.get(`http://127.0.0.1:8000/api/chart/attendance?${q}`)
      .then(res => {
        const aggr = res.data.labels.map((label, idx) => ({
          grado: label.replace(' PRIMARIA - PRIMARIA', 'P').replace(' SECUNDARIA - SECUNDARIA', 'S'),
          asistencias: res.data.asistencias[idx],
          ausencias: res.data.ausencias[idx]
        }));
        setAsistenciaData(aggr);
      })
      .catch(console.error);

    // Fetch Docentes
    axios.get(`http://127.0.0.1:8000/api/docentes?${q}`)
      .then(res => {
        // Top 5 docentes
        const top5 = res.data.slice(0, 5);
        setDocentesData(top5);
      })
      .catch(console.error);
  }, [filters]);

  const PIE_COLORS = ['#2d8a56', '#c23b3b'];

  return (
    <div className="vista-resumen">
      <KpiCards filters={filters} />
      
      <div className="dashboard-cover-grid">
        
        {/* Pie Chart: Aprobación */}
        <div className="card">
          <h3><i className="fa-solid fa-chart-pie"></i> Ratio de Aprobación</h3>
          <div className="chart-container" style={{ height: 250 }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={aprobadosData} innerRadius={60} outerRadius={90} paddingAngle={5} dataKey="value">
                  {aprobadosData.map((entry, index) => <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />)}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', color: '#3b1e27' }} />
                <Legend verticalAlign="bottom" height={36}/>
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Area Chart: Asistencia por Grado */}
        <div className="card">
          <h3><i className="fa-solid fa-calendar-check"></i> Asistencias vs Ausencias</h3>
          <div className="chart-container" style={{ height: 250 }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={asistenciaData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorAsistencia" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#2d8a56" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#2d8a56" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorAusencia" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#c23b3b" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#c23b3b" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.05)" />
                <XAxis dataKey="grado" tick={{fontSize: 10}} stroke="#5b2133" />
                <YAxis stroke="#5b2133" tick={{fontSize: 10}} />
                <Tooltip contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', color: '#3b1e27' }} />
                <Area type="monotone" dataKey="asistencias" stroke="#2d8a56" fillOpacity={1} fill="url(#colorAsistencia)" />
                <Area type="monotone" dataKey="ausencias" stroke="#c23b3b" fillOpacity={1} fill="url(#colorAusencia)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Bar Chart Horizontal: Docentes */}
        <div className="card full-width">
          <h3><i className="fa-solid fa-chalkboard-user"></i> Top 5 Docentes Destacados</h3>
          <div className="chart-container" style={{ height: 250 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart layout="vertical" data={docentesData} margin={{ top: 5, right: 30, left: 100, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} stroke="rgba(0,0,0,0.05)" />
                <XAxis type="number" domain={[0, 20]} stroke="#5b2133" />
                <YAxis dataKey="profesor" type="category" stroke="#5b2133" tick={{fontSize: 11}} width={120} />
                <Tooltip contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', color: '#3b1e27' }} />
                <Bar dataKey="promedio" fill="#8b3a53" radius={[0, 4, 4, 0]} barSize={20} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>
    </div>
  );
}

export default VistaResumenKpis;
