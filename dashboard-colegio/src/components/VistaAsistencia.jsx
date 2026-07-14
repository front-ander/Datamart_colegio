import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

function VistaAsistencia({ filters }) {
  const [data, setData] = useState([]);

  useEffect(() => {
    const params = new URLSearchParams();
    if (filters?.anio) params.append('anio', filters.anio);
    if (filters?.grado) params.append('grado', filters.grado);

    axios.get(`http://127.0.0.1:8000/api/asistencia-detallada?${params.toString()}`)
      .then(res => setData(res.data))
      .catch(err => console.error(err));
  }, [filters]);

  return (
    <div className="tab-content">
      <div className="table-card" style={{ marginBottom: '16px' }}>
        <h3>Tendencia de Ausentismo y Tardanzas</h3>
        <div style={{ height: 300 }}>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data}>
              <defs>
                <linearGradient id="colorAusencia" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ef4444" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="colorTardanza" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#f59e0b" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="Año" tick={{ fontSize: 12, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 12, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
              <Tooltip cursor={{ fill: 'rgba(255,255,255,0.05)' }} contentStyle={{ backgroundColor: '#252648', borderColor: 'rgba(255,255,255,0.1)', color: '#fff' }} />
              <Legend wrapperStyle={{ color: '#94a3b8' }} />
              <Area type="monotone" dataKey="ausencias" stroke="#ef4444" strokeWidth={3} fillOpacity={1} fill="url(#colorAusencia)" dot={{ r: 4 }} activeDot={{ r: 6 }} />
              <Area type="monotone" dataKey="tardanzas" stroke="#f59e0b" strokeWidth={3} fillOpacity={1} fill="url(#colorTardanza)" dot={{ r: 4 }} activeDot={{ r: 6 }} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
      
      <div className="table-card card full-width">
        <h3>Tabla Detallada de Asistencia (Anual)</h3>
        <div className="table-container">
          <table className="data-table">
            <thead>
            <tr>
              <th>Año</th>
              <th>Total Asistencias</th>
              <th>Total Ausencias</th>
              <th>Total Tardanzas</th>
              <th>Tasa Ausentismo</th>
            </tr>
          </thead>
          <tbody>
            {data.map((row, i) => {
              const total = row.asistencias + row.ausencias + row.tardanzas;
              const tasaAusentismo = total > 0 ? (row.ausencias / total) * 100 : 0;
              return (
                <tr key={i}>
                  <td>{row.Año}</td>
                  <td>{row.asistencias}</td>
                  <td>{row.ausencias}</td>
                  <td>{row.tardanzas}</td>
                  <td>
                    <span className={`status-badge ${tasaAusentismo > 10 ? 'status-danger' : 'status-good'}`}>
                      {tasaAusentismo.toFixed(2)}%
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default VistaAsistencia;
