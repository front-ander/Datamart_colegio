import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

function VistaGradosAcademicos({ filters }) {
  const [data, setData] = useState([]);

  useEffect(() => {
    const params = new URLSearchParams();
    if (filters?.anio) params.append('anio', filters.anio);
    if (filters?.grado) params.append('grado', filters.grado);

    axios.get(`http://127.0.0.1:8000/api/riesgo?${params.toString()}`)
      .then(res => {
        const aggr = {};
        res.data.forEach(d => {
          if(!aggr[d.grado]) aggr[d.grado] = { Grado: d.grado, total_riesgo: 0 };
          aggr[d.grado].total_riesgo += d.promedio_notas < 11 ? 1 : 0;
        });
        setData(Object.values(aggr));
      })
      .catch(err => console.error(err));
  }, [filters]);

  return (
    <div className="card full-width">
      <h3><i className="fa-solid fa-graduation-cap"></i> Riesgo por Grado Académico</h3>
      <div className="chart-container">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.1)" />
            <XAxis dataKey="Grado" stroke="#5b2133" />
            <YAxis stroke="#5b2133" />
            <Tooltip contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', color: '#3b1e27' }} />
            <Bar dataKey="total_riesgo" fill="#d97706" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
export default VistaGradosAcademicos;
