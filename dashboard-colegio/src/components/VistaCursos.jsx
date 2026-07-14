import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

function VistaCursos({ filters }) {
  const [data, setData] = useState([]);

  useEffect(() => {
    const params = new URLSearchParams();
    if (filters?.anio) params.append('anio', filters.anio);
    if (filters?.grado) params.append('grado', filters.grado);

    axios.get(`http://127.0.0.1:8000/api/chart/grades?${params.toString()}`)
      .then(res => {
        const formatted = res.data.labels.map((label, idx) => ({
          name: label,
          promedio: res.data.data[idx]
        }));
        setData(formatted);
      })
      .catch(err => console.error(err));
  }, [filters]);

  return (
    <div className="card full-width">
      <h3><i className="fa-solid fa-book-open"></i> Distribución de Cursos y Promedios</h3>
      <div className="chart-container">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.1)" />
            <XAxis dataKey="name" stroke="#5b2133" tick={{fontSize: 10}} angle={-45} textAnchor="end" height={80} />
            <YAxis stroke="#5b2133" domain={[0, 20]} />
            <Tooltip contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', color: '#3b1e27' }} />
            <Bar dataKey="promedio" fill="#8b3a53" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
export default VistaCursos;
