import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

function VistaRendimientoAnual({ filters }) {
  const [data, setData] = useState([]);

  useEffect(() => {
    const params = new URLSearchParams();
    if (filters?.anio) params.append('anio', filters.anio);
    if (filters?.grado) params.append('grado', filters.grado);

    axios.get(`http://127.0.0.1:8000/api/rendimiento?${params.toString()}`)
      .then(res => setData(res.data))
      .catch(err => console.error(err));
  }, [filters]);

  return (
    <div className="tab-content">
      <div className="table-card" style={{ marginBottom: '16px' }}>
        <h3>Evolución Histórica de Aprobación</h3>
        <div style={{ height: 300 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="Año" tick={{ fontSize: 12, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 12, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
              <Tooltip cursor={{ fill: 'rgba(255,255,255,0.05)' }} contentStyle={{ backgroundColor: '#252648', borderColor: 'rgba(255,255,255,0.1)', color: '#fff' }} />
              <Legend wrapperStyle={{ color: '#94a3b8' }} />
              <Bar dataKey="aprobados" stackId="a" fill="#10b981" barSize={40} />
              <Bar dataKey="desaprobados" stackId="a" fill="#ef4444" barSize={40} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
      
      <div className="table-card card full-width">
        <h3>Tabla Detallada de Rendimiento por Año</h3>
        <div className="table-container">
          <table className="data-table">
            <thead>
            <tr>
              <th>Año</th>
              <th>Total Estudiantes</th>
              <th>Aprobados</th>
              <th>Desaprobados</th>
              <th>Tasa Aprobación</th>
            </tr>
          </thead>
          <tbody>
            {data.map((row, i) => (
              <tr key={i}>
                <td>{row.Año}</td>
                <td>{row.total}</td>
                <td>{row.aprobados}</td>
                <td>{row.desaprobados}</td>
                <td>
                  <span className={`status-badge ${row.aprobados / row.total >= 0.5 ? 'status-good' : 'status-danger'}`}>
                    {Math.round((row.aprobados / row.total) * 100)}%
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default VistaRendimientoAnual;
